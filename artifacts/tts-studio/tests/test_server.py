import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave
import xml.etree.ElementTree as ET

SERVER = Path(__file__).resolve().parents[1] / 'server' / 'tts_server.py'
spec = importlib.util.spec_from_file_location('tts_server', SERVER)
tts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tts)


def wav_bytes():
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(24000)
        audio.writeframes(b'\x00\x00' * 240)
    return buf.getvalue()


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = tempfile.TemporaryDirectory()
        source = Path(cls.fixture.name) / 'test.wav'
        target = Path(cls.fixture.name) / 'test.mp3'
        source.write_bytes(wav_bytes())
        executable = tts.ffmpeg_path()
        if not executable:
            raise unittest.SkipTest('Install imageio-ffmpeg or ffmpeg for audio validation tests.')
        subprocess.run([executable, '-v', 'error', '-i', str(source), str(target)], check=True, capture_output=True)
        cls.mp3 = target.read_bytes()

    @classmethod
    def tearDownClass(cls):
        cls.fixture.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.env = patch.dict(os.environ, {'TTS_OUTPUT_DIR': self.temp.name}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_offline_blocks_cloud_before_network_or_file_write(self):
        for provider in ['azure', 'elevenlabs', 'speech-api', 'edge', 'youdao', 'dashscope']:
            with patch.object(tts, 'request') as network:
                with self.assertRaisesRegex(ValueError, 'offline_only'):
                    tts.synthesize(provider, 'Private text')
                network.assert_not_called()
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_invalid_inputs_never_render(self):
        with patch.object(tts, 'render') as render:
            for kwargs in [{'text': ''}, {'text': 'x' * 3001}, {'text': 'a', 'speed': float('nan')},
                           {'text': 'a', 'speed': True}, {'text': 'a', 'offline_only': 'false'},
                           {'text': 'a', 'format': 'mp3'}, {'text': 'a', 'voice': 3}]:
                with self.assertRaises(ValueError):
                    tts.synthesize('windows', **kwargs)
            render.assert_not_called()

    def test_windows_payload_does_not_interpolate_user_text_as_code(self):
        text = "你好 '; $(Get-Item secret); <speak> & hello"
        def fake_windows(payload):
            self.assertEqual(payload['text'], text)
            Path(payload['output']).write_bytes(wav_bytes())
        with patch.object(tts, 'windows_call', side_effect=fake_windows) as call:
            first = tts.synthesize('windows', text, voice='Local Voice')
            second = tts.synthesize('windows', text, voice='Local Voice')
        self.assertEqual(call.call_count, 1)
        self.assertFalse(first['cached'])
        self.assertTrue(second['cached'])
        self.assertEqual(first['duration'], 0.01)
        self.assertEqual(first['sha256'], second['sha256'])

    def test_azure_ssml_roundtrips_plain_text_and_auth(self):
        os.environ.update(AZURE_SPEECH_KEY='not-a-real-key', AZURE_SPEECH_REGION='eastasia')
        text = '你好 <voice name="evil"> & 2026年10月15日'
        def fake_request(url, headers, body):
            self.assertEqual(url, 'https://eastasia.tts.speech.microsoft.com/cognitiveservices/v1')
            self.assertEqual(headers['Ocp-Apim-Subscription-Key'], 'not-a-real-key')
            xml = ET.fromstring(body)
            self.assertEqual(''.join(xml.itertext()), text)
            self.assertEqual(len(list(xml.iter('voice'))), 1)
            return wav_bytes()
        with patch.object(tts, 'request', side_effect=fake_request):
            result = tts.synthesize('azure', text, offline_only=False)
        self.assertFalse(result['offline'])

    def test_invalid_provider_audio_never_published_or_cached(self):
        os.environ.update(AZURE_SPEECH_KEY='test', AZURE_SPEECH_REGION='eastasia')
        with patch.object(tts, 'request', return_value=b'{"error":"quota"}'):
            with self.assertRaisesRegex(ValueError, 'WAV'):
                tts.synthesize('azure', 'hello', offline_only=False)
        self.assertEqual(list(Path(self.temp.name).iterdir()), [])

    def test_elevenlabs_mp3_request_and_voice_escaping(self):
        os.environ.update(ELEVENLABS_API_KEY='test', ELEVENLABS_MODEL_ID='selected-model')
        with patch.object(tts, 'request', return_value=self.mp3) as call:
            result = tts.synthesize('elevenlabs', 'hello', voice='a/b', format='mp3', offline_only=False)
        url, headers, body = call.call_args.args
        self.assertIn('a%2Fb?', url)
        self.assertEqual(json.loads(body)['model_id'], 'selected-model')
        self.assertGreater(result['duration'], 0)
        self.assertEqual(result['validation'], 'decoded')

    def test_speech_api_configuration_and_body(self):
        os.environ.update(TTS_SPEECH_URL='https://example.test/v1/audio/speech', TTS_SPEECH_API_KEY='test',
                          TTS_SPEECH_MODEL='selected', TTS_SPEECH_VOICE='voice')
        with patch.object(tts, 'request', return_value=wav_bytes()) as call:
            tts.synthesize('speech-api', 'hello', offline_only=False)
        self.assertEqual(json.loads(call.call_args.args[2])['response_format'], 'wav')
        for url in ['http://localhost:8000/speech', 'https://user:pass@example.test/speech', 'https://example.test/#x']:
            os.environ['TTS_SPEECH_URL'] = url
            with self.assertRaises(ValueError):
                tts.speech_endpoint()

    def test_sherpa_requires_local_assets(self):
        path = Path(self.temp.name) / 'config.json'
        path.write_text(json.dumps({'model': {'vits': {'model': 'https://example.test/model.onnx'}}}))
        os.environ['TTS_SHERPA_CONFIG'] = str(path)
        with self.assertRaisesRegex(ValueError, 'absolute local'):
            tts.sherpa_config()

    def test_tool_errors_do_not_leak_http_response_bodies(self):
        with patch.object(tts, 'call_tool', side_effect=RuntimeError('SECRET VALUE')):
            response = tts.dispatch({'id': 1, 'method': 'tools/call', 'params': {'name': 'tts_doctor'}})
        self.assertTrue(response['result']['isError'])
        self.assertNotIn('SECRET VALUE', json.dumps(response))

    def test_mcp_stdio_handshake_discovery_and_harmless_call(self):
        messages = [
            {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-06-18'}},
            {'jsonrpc': '2.0', 'method': 'notifications/initialized'},
            {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'},
            {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'tts_doctor', 'arguments': {}}},
            {'jsonrpc': '2.0', 'id': 4, 'method': 'tools/call', 'params': {'name': 'tts_catalog', 'arguments': {}}}
        ]
        proc = subprocess.run([sys.executable, str(SERVER)], input=''.join(json.dumps(m) + '\n' for m in messages),
                              text=True, capture_output=True, timeout=20)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        results = [json.loads(line) for line in proc.stdout.splitlines()]
        self.assertEqual([r['id'] for r in results], [1, 2, 3, 4])
        self.assertEqual(len(results[1]['result']['tools']), 5)
        self.assertFalse(results[2]['result']['isError'])
        catalog = json.loads(results[3]['result']['content'][0]['text'])
        self.assertEqual(len(catalog['offline']), 15)
        self.assertEqual(len(catalog['online']), 15)

    def test_fake_mp3_and_truncated_wav_rejected(self):
        bad = Path(self.temp.name) / 'bad.mp3'
        bad.write_bytes(b'ID3testaudio')
        with self.assertRaisesRegex(ValueError, 'undecodable'):
            tts.audio_info(bad, 'mp3')
        bad = bad.with_suffix('.wav')
        bad.write_bytes(wav_bytes()[:-20])
        with self.assertRaisesRegex(ValueError, 'truncated'):
            tts.audio_info(bad, 'wav')

    def test_youdao_encoding_and_no_secret(self):
        with patch.object(tts, 'request', return_value=self.mp3) as call:
            result = tts.synthesize('youdao', 'good morning', voice='en-GB', format='mp3', offline_only=False)
        query = tts.urllib.parse.parse_qs(tts.urllib.parse.urlsplit(call.call_args.args[0]).query)
        self.assertEqual(query, {'type': ['1'], 'audio': ['good morning']})
        self.assertEqual(result['actualProvider'], 'youdao')
        self.assertIsNone(result['fallbackReason'])
        with self.assertRaisesRegex(ValueError, 'word/short-phrase'):
            tts.synthesize('youdao', 'This is a sentence.', format='mp3', offline_only=False)

    def test_dashscope_region_body_and_download_without_auth(self):
        os.environ.update(DASHSCOPE_API_KEY='test', TTS_DASHSCOPE_MODEL='qwen3-tts-flash', TTS_DASHSCOPE_VOICE='Cherry')
        response = json.dumps({'output': {'audio': {'url': 'http://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/test.wav?signature=test'}}}).encode()
        with patch.object(tts, 'request', side_effect=[response, wav_bytes()]) as call:
            tts.synthesize('dashscope', 'Hello', offline_only=False)
        first, second = call.call_args_list
        self.assertIn('dashscope.aliyuncs.com', first.args[0])
        self.assertEqual(json.loads(first.args[2])['input']['text'], 'Hello')
        self.assertTrue(second.args[0].startswith('https://'))
        self.assertNotIn('Authorization', second.args[1])

    def test_dashscope_rejects_unexpected_download_host(self):
        os.environ.update(DASHSCOPE_API_KEY='test', TTS_DASHSCOPE_MODEL='qwen3-tts-flash', TTS_DASHSCOPE_VOICE='Cherry')
        response = json.dumps({'output': {'audio': {'url': 'https://example.test/audio.wav'}}}).encode()
        with patch.object(tts, 'request', return_value=response) as call:
            with self.assertRaisesRegex(ValueError, 'host'):
                tts.dashscope_audio('Hello', '')
        self.assertEqual(call.call_count, 1)

    def test_edge_proxy_voice_and_rate(self):
        from types import SimpleNamespace
        calls = []
        class FakeCommunicate:
            def __init__(inner, text, voice, **kwargs):
                calls.append((text, voice, kwargs))
            async def save(inner, path):
                Path(path).write_bytes(self.mp3)
        os.environ['TTS_EDGE_PROXY'] = 'http://127.0.0.1:9999'
        with patch.dict(sys.modules, {'edge_tts': SimpleNamespace(Communicate=FakeCommunicate)}):
            result = tts.synthesize('edge', 'Hello', voice='en-US-AriaNeural', speed=1.2, format='mp3', offline_only=False)
        self.assertEqual(calls[0][2]['rate'], '+20%')
        self.assertEqual(calls[0][2]['proxy'], os.environ['TTS_EDGE_PROXY'])
        self.assertEqual(result['actualProvider'], 'edge')

    def test_macos_uses_file_and_argument_array(self):
        def fake_run(args, **kwargs):
            self.assertNotIn('hello; rm', args)
            self.assertEqual(Path(args[args.index('-f') + 1]).read_text(encoding='utf-8'), 'hello; rm')
            Path(args[args.index('-o') + 1]).write_bytes(wav_bytes())
            return subprocess.CompletedProcess(args, 0)
        with patch.object(tts.sys, 'platform', 'darwin'), patch.object(tts.shutil, 'which', return_value='/usr/bin/say'), patch.object(tts.subprocess, 'run', side_effect=fake_run):
            tts.synthesize('macos', 'hello; rm', voice='Samantha')

    def test_batch_split_resume_and_playlist(self):
        text = 'A sentence. ' * 600
        chunks = tts.split_text(text, 600)
        self.assertEqual(''.join(chunks), text)
        self.assertTrue(all(len(c) <= 600 for c in chunks))
        def fake_windows(payload):
            Path(payload['output']).write_bytes(wav_bytes())
        with patch.object(tts, 'windows_call', side_effect=fake_windows):
            result = tts.synthesize_batch('windows', text)
            rerun = tts.synthesize_batch('windows', text)
        self.assertTrue(Path(result['playlistPath']).exists())
        self.assertTrue(all(c['cached'] for c in rerun['clips']))

    def test_doctor_distinguishes_platform_from_configuration(self):
        with patch.object(tts.sys, 'platform', 'linux'):
            result = tts.doctor()
        self.assertFalse(result['providers']['windows']['platformSupported'])
        self.assertFalse(result['providers']['macos']['platformSupported'])
        self.assertFalse(result['providers']['dashscope']['configurationPresent'])

    def test_malformed_rpc_params_are_not_parse_error(self):
        response = tts.dispatch({'id': 1, 'method': 'initialize', 'params': []})
        self.assertEqual(response['error']['code'], -32602)

    def test_batch_stops_on_failure_without_switching_provider(self):
        calls = []
        def fake_synthesize(provider, text, *args):
            calls.append(provider)
            if len(calls) == 2:
                raise ValueError('temporary failure')
            return {'path': str(Path(self.temp.name) / 'clip.wav')}
        with patch.object(tts, 'synthesize', side_effect=fake_synthesize):
            with self.assertRaisesRegex(ValueError, 'stopped at clip 2'):
                tts.synthesize_batch('azure', 'A long sentence. ' * 600, offline_only=False)
        self.assertEqual(calls, ['azure', 'azure'])

    def test_corrupted_cache_is_regenerated(self):
        def fake_windows(payload):
            Path(payload['output']).write_bytes(wav_bytes())
        with patch.object(tts, 'windows_call', side_effect=fake_windows) as render:
            first = tts.synthesize('windows', 'Hello')
            Path(first['path']).write_bytes(b'broken')
            second = tts.synthesize('windows', 'Hello')
        self.assertEqual(render.call_count, 2)
        self.assertFalse(second['cached'])


if __name__ == '__main__':
    unittest.main()
