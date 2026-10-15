"""Dependency-free MCP stdio server and CLI. Python 3.10+. No model downloads."""
import argparse
import contextlib
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import wave
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.2.0'
OFFLINE = {'windows', 'macos', 'sherpa'}
PROVIDERS = ['edge', 'youdao', 'dashscope', 'macos', 'sherpa', 'azure', 'elevenlabs', 'speech-api', 'windows']
MIME = {'wav': 'audio/wav', 'mp3': 'audio/mpeg'}
FORMATS = {p: ['wav'] if p in OFFLINE or p == 'dashscope' else ['mp3'] if p in {'edge', 'youdao', 'elevenlabs'} else ['wav', 'mp3'] for p in PROVIDERS}
MODEL_CACHE = {}


def ffmpeg_path():
    configured = os.environ.get('TTS_FFMPEG')
    if configured:
        return configured if Path(configured).is_file() else None
    found = shutil.which('ffmpeg')
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError):
        return None


def macos_call(text, voice, speed, output):
    if sys.platform != 'darwin' or not shutil.which('say'):
        raise ValueError('macos provider requires macOS and an installed system voice.')
    with tempfile.TemporaryDirectory(prefix='tts-studio-') as folder:
        source = Path(folder) / 'text.txt'
        source.write_text(text, encoding='utf-8')
        args = ['say', '-f', str(source), '-o', str(output), '--file-format=WAVE', '--data-format=LEI16@24000', '-r', str(round(175 * speed))]
        if voice:
            args += ['-v', voice]
        result = subprocess.run(args, capture_output=True, timeout=120)
        if result.returncode:
            raise ValueError('macOS speech failed; install/select a local voice with say -v "?".')


async def edge_generate(text, voice, speed, output):
    import asyncio
    try:
        import edge_tts
    except ImportError:
        raise ValueError('Install edge-tts in this server Python environment.') from None
    communicator = edge_tts.Communicate(
        text, voice or os.environ.get('TTS_EDGE_VOICE', 'en-US-AriaNeural'),
        rate=f'{round((speed - 1) * 100):+d}%', proxy=os.environ.get('TTS_EDGE_PROXY') or None,
        connect_timeout=10, receive_timeout=60)
    try:
        await asyncio.wait_for(communicator.save(str(output)), timeout=120)
    except Exception:
        raise ValueError('Edge synthesis failed; check network, voice and TTS_EDGE_PROXY. No provider switch.') from None


def dashscope_audio(text, voice):
    region = os.environ.get('TTS_DASHSCOPE_REGION', 'beijing')
    hosts = {'beijing': 'dashscope.aliyuncs.com', 'singapore': 'dashscope-intl.aliyuncs.com'}
    if region not in hosts:
        raise ValueError('TTS_DASHSCOPE_REGION must be beijing or singapore; match your API key.')
    body = {'model': required('TTS_DASHSCOPE_MODEL'), 'input': {
        'text': text, 'voice': voice or required('TTS_DASHSCOPE_VOICE'),
        'language_type': os.environ.get('TTS_DASHSCOPE_LANGUAGE', 'Auto')}}
    response = json.loads(request(f'https://{hosts[region]}/api/v1/services/aigc/multimodal-generation/generation',
        {'Authorization': 'Bearer ' + required('DASHSCOPE_API_KEY'), 'Content-Type': 'application/json'}, json.dumps(body).encode()))
    try:
        url = response['output']['audio']['url']
    except (KeyError, TypeError):
        raise ValueError('DashScope returned no audio URL; check selected Qwen-TTS model and voice.') from None
    parsed = urllib.parse.urlsplit(url)
    # Only signed provider object-storage URLs; never forward the API key to downloads.
    if parsed.scheme not in {'http', 'https'} or parsed.username or parsed.password or parsed.fragment or not re.fullmatch(r'dashscope-result-[a-z0-9-]+\.oss-[a-z0-9-]+\.aliyuncs\.com', parsed.hostname or ''):
        raise ValueError('Unexpected DashScope audio host; download blocked.')
    url = urllib.parse.urlunsplit(('https', parsed.netloc, parsed.path, parsed.query, ''))
    return request(url, {'Accept': 'audio/wav'})


def required(name):
    value = os.environ.get(name, '').strip()
    if not value:
        raise ValueError(f'Set {name} in the server environment.')
    return value


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Redirect refused; configure the final endpoint explicitly.')


def request(url, headers, body=None):
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=60) as response:
            data = response.read(32 * 1024 * 1024 + 1)
            if len(data) > 32 * 1024 * 1024:
                raise ValueError('Audio response exceeds 32 MiB; split the text.')
            return data
    except urllib.error.HTTPError as error:
        # Provider response bodies can echo text or credentials; do not log them.
        raise ValueError(f'TTS provider HTTP {error.code}; check credentials, quota, model and voice. No automatic retry.') from None
    except urllib.error.URLError:
        raise ValueError('TTS network request failed; check connectivity and endpoint. No automatic retry.') from None


def speech_endpoint():
    url = required('TTS_SPEECH_URL')
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.fragment or parsed.query:
        raise ValueError('TTS_SPEECH_URL must be an HTTPS speech endpoint without credentials, query or fragment.')
    return url


def windows_call(payload):
    if sys.platform != 'win32':
        raise ValueError('The windows provider requires Windows desktop and an installed SAPI voice.')
    with tempfile.TemporaryDirectory(prefix='tts-studio-') as folder:
        source = Path(folder) / 'request.json'
        source.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
        command = [
            'powershell.exe', '-NoProfile', '-NonInteractive', '-File',
            str(ROOT / 'server' / 'windows-speech.ps1'), '-RequestPath', str(source)
        ]
        try:
            result = subprocess.run(command, capture_output=True, timeout=120)
        except subprocess.TimeoutExpired:
            raise ValueError('Windows synthesis timed out.') from None
        if result.returncode:
            raise ValueError('Windows speech failed; check installed SAPI voices with tts_voices. No cloud fallback.')
        return json.loads(result.stdout.decode('utf-8-sig').strip())


def sherpa_config():
    path = Path(required('TTS_SHERPA_CONFIG')).expanduser().resolve()
    config = json.loads(path.read_text(encoding='utf-8-sig'))
    families = set(config.get('model', {})) & {'vits', 'matcha', 'kokoro'}
    if len(families) != 1:
        raise ValueError('Configure exactly one supported sherpa family: vits, matcha or kokoro.')
    if config.get('model', {}).get('debug'):
        raise ValueError('Disable sherpa debug logging for MCP stdio use.')
    # Explicit absolute file paths make behavior independent of host working directory.
    for section in config.get('model', {}).values():
        if isinstance(section, dict):
            for key, value in section.items():
                if isinstance(value, str) and value and key != 'provider':
                    if not Path(value).is_absolute() or not Path(value).exists():
                        raise ValueError(f'Sherpa {key} must be an existing absolute local path.')
    for key in ['rule_fsts', 'rule_fars']:
        for value in config.get(key, '').split(','):
            if value and (not Path(value).is_absolute() or not Path(value).exists()):
                raise ValueError(f'Sherpa {key} requires existing absolute local paths.')
    return config


def render(provider, text, voice, speed, fmt, output):
    if provider == 'edge':
        import asyncio
        asyncio.run(edge_generate(text, voice, speed, output))
    elif provider == 'youdao':
        kind = {'en-US': 2, 'en-GB': 1}[voice or 'en-US']
        query = urllib.parse.urlencode({'type': kind, 'audio': text})
        output.write_bytes(request('https://dict.youdao.com/dictvoice?' + query,
                                  {'User-Agent': 'Mozilla/5.0', 'Accept': 'audio/mpeg'}))
    elif provider == 'dashscope':
        output.write_bytes(dashscope_audio(text, voice))
    elif provider == 'macos':
        macos_call(text, voice, speed, output)
    elif provider == 'windows':
        windows_call({'action': 'synthesize', 'text': text, 'voice': voice,
                      'rate': max(-10, min(10, round(10 * math.log2(speed)))), 'output': str(output)})
    elif provider == 'sherpa':
        try:
            import sherpa_onnx
        except ImportError:
            raise ValueError('Install sherpa-onnx in the Python environment used by this server.') from None
        settings = sherpa_config()
        model = dict(settings.pop('model'))
        classes = {'vits': 'OfflineTtsVitsModelConfig', 'matcha': 'OfflineTtsMatchaModelConfig',
                   'kokoro': 'OfflineTtsKokoroModelConfig'}
        for family, cls in classes.items():
            if family in model:
                model[family] = getattr(sherpa_onnx, cls)(**model[family])
        config = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(**model), **settings)
        if not config.validate():
            raise ValueError('Sherpa configuration failed validation.')
        cache_key = json.dumps(sherpa_config(), sort_keys=True) + os.environ.get('TTS_CACHE_REVISION', '1')
        if cache_key not in MODEL_CACHE:
            MODEL_CACHE.clear()  # Bound resident memory to one model.
            MODEL_CACHE[cache_key] = sherpa_onnx.OfflineTts(config)
        tts = MODEL_CACHE[cache_key]
        sid = int(voice or '0')
        if sid < 0 or sid >= tts.num_speakers:
            raise ValueError('Speaker ID is outside the loaded model range.')
        audio = tts.generate(text, sid=sid, speed=speed)
        if not sherpa_onnx.write_wave(str(output), audio.samples, audio.sample_rate):
            raise ValueError('Sherpa could not save WAV output.')
    elif provider == 'azure':
        region = required('AZURE_SPEECH_REGION')
        if not re.fullmatch(r'[a-z0-9-]+', region):
            raise ValueError('Invalid Azure Speech region.')
        voice = voice or os.environ.get('AZURE_SPEECH_VOICE', 'zh-CN-XiaoxiaoNeural')
        lang = os.environ.get('AZURE_SPEECH_LANGUAGE', 'zh-CN')
        ssml = (f'<speak version="1.0" xml:lang={quoteattr(lang)}>'
                f'<voice name={quoteattr(voice)}><prosody rate="{(speed-1)*100:+.0f}%">'
                f'{escape(text)}</prosody></voice></speak>')
        headers = {'Ocp-Apim-Subscription-Key': required('AZURE_SPEECH_KEY'),
                   'Content-Type': 'application/ssml+xml', 'User-Agent': 'tts-studio',
                   'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm' if fmt == 'wav' else 'audio-24khz-48kbitrate-mono-mp3'}
        output.write_bytes(request(f'https://{region}.tts.speech.microsoft.com/cognitiveservices/v1', headers, ssml.encode('utf-8')))
    elif provider == 'elevenlabs':
        if speed != 1:
            raise ValueError('This ElevenLabs adapter currently supports speed=1 only.')
        voice = voice or required('ELEVENLABS_VOICE_ID')
        body = json.dumps({'text': text, 'model_id': required('ELEVENLABS_MODEL_ID')}).encode()
        url = 'https://api.elevenlabs.io/v1/text-to-speech/' + urllib.parse.quote(voice, safe='') + '?output_format=mp3_44100_128'
        output.write_bytes(request(url, {'xi-api-key': required('ELEVENLABS_API_KEY'), 'Content-Type': 'application/json'}, body))
    elif provider == 'speech-api':
        body = {'model': required('TTS_SPEECH_MODEL'), 'input': text,
                'voice': voice or required('TTS_SPEECH_VOICE'), 'response_format': fmt, 'speed': speed}
        output.write_bytes(request(speech_endpoint(), {'Authorization': 'Bearer ' + required('TTS_SPEECH_API_KEY'),
                           'Content-Type': 'application/json'}, json.dumps(body).encode()))


def audio_info(path, fmt):
    data = path.read_bytes()
    if fmt == 'wav':
        if data[:4] != b'RIFF' or data[8:12] != b'WAVE':
            raise ValueError('Provider did not return a WAV file.')
        with wave.open(str(path), 'rb') as audio:
            if not audio.getnframes():
                raise ValueError('Provider returned empty audio.')
            expected = audio.getnframes() * audio.getnchannels() * audio.getsampwidth()
            count = 0
            while block := audio.readframes(65536):
                count += len(block)
            if count != expected:
                raise ValueError('Provider returned truncated WAV audio.')
            return {'sampleRate': audio.getframerate(), 'duration': audio.getnframes() / audio.getframerate()}
    if not (data.startswith(b'ID3') or (len(data) > 2 and data[0] == 255 and data[1] & 224 == 224)):
        raise ValueError('Provider did not return an MP3 file.')
    executable = ffmpeg_path()
    if not executable:
        raise ValueError('MP3 validation requires ffmpeg or imageio-ffmpeg; install before synthesis.')
    with tempfile.TemporaryDirectory(prefix='tts-decode-') as folder:
        pcm = Path(folder) / 'decoded.pcm'
        try:
            decoded = subprocess.run([executable, '-nostdin', '-v', 'error', '-xerror', '-i', str(path),
                '-map', '0:a:0', '-ac', '1', '-ar', '24000', '-f', 's16le', str(pcm)],
                capture_output=True, timeout=120)
        except subprocess.TimeoutExpired:
            raise ValueError('Audio decoding timed out.') from None
        if decoded.returncode or not pcm.exists() or not pcm.stat().st_size:
            raise ValueError('Provider returned undecodable MP3 audio.')
        return {'sampleRate': None, 'duration': pcm.stat().st_size / 48000, 'validation': 'decoded', 'decodedSampleRate': 24000}


def synthesize(provider, text, voice='', speed=1.0, format='wav', offline_only=True):
    if provider not in PROVIDERS:
        raise ValueError('Unknown provider.')
    if type(offline_only) is not bool:
        raise ValueError('offline_only must be a boolean.')
    if offline_only and provider not in OFFLINE:
        raise ValueError('offline_only blocks cloud providers; explicitly set offline_only=false to send text online.')
    if not isinstance(text, str) or not text.strip() or len(text) > 3000:
        raise ValueError('Provide 1–3000 characters; split longer text into separate files.')
    if not isinstance(voice, str) or len(voice) > 200:
        raise ValueError('voice must be a string of at most 200 characters.')
    if type(speed) not in (int, float) or not math.isfinite(speed) or not 0.5 <= speed <= 2:
        raise ValueError('speed must be between 0.5 and 2.')
    if format not in FORMATS[provider]:
        raise ValueError(f'{provider} supports these formats: {FORMATS[provider]}.')
    if provider == 'youdao' and (len(text) > 100 or not re.fullmatch(r"[A-Za-z][A-Za-z '\-]*", text) or len(text.split()) > 8):
        raise ValueError('Youdao supports English word/short-phrase lookup here (up to 8 words / 100 characters), not arbitrary sentences.')
    if provider == 'youdao' and voice not in {'', 'en-US', 'en-GB'}:
        raise ValueError('Youdao voice must be en-US or en-GB.')
    if provider in {'youdao', 'dashscope', 'elevenlabs'} and speed != 1:
        raise ValueError(f'{provider} adapter currently supports speed=1 only.')
    if provider == 'dashscope' and len(text) > 600:
        raise ValueError('Qwen-TTS supports at most 600 characters per clip; use tts_synthesize_batch.')
    if format == 'mp3' and not ffmpeg_path():
        raise ValueError('Install ffmpeg or imageio-ffmpeg before generating MP3.')
    # Cloud output is cached by request and non-secret account/model configuration.
    keys = {'windows': [], 'macos': [], 'edge': ['TTS_EDGE_VOICE'], 'youdao': [],
            'dashscope': ['TTS_DASHSCOPE_REGION', 'TTS_DASHSCOPE_MODEL', 'TTS_DASHSCOPE_VOICE', 'TTS_DASHSCOPE_LANGUAGE'],
            'sherpa': ['TTS_SHERPA_CONFIG'],
            'azure': ['AZURE_SPEECH_REGION', 'AZURE_SPEECH_VOICE', 'AZURE_SPEECH_LANGUAGE'],
            'elevenlabs': ['ELEVENLABS_MODEL_ID', 'ELEVENLABS_VOICE_ID'],
            'speech-api': ['TTS_SPEECH_URL', 'TTS_SPEECH_MODEL', 'TTS_SPEECH_VOICE']}[provider]
    identity = {k: os.environ.get(k, '') for k in keys}
    if provider == 'sherpa':
        identity['config'] = sherpa_config()
    identity['revision'] = os.environ.get('TTS_CACHE_REVISION', '1')
    digest = hashlib.sha256(json.dumps([provider, text, voice, speed, format, identity], sort_keys=True).encode()).hexdigest()
    directory = Path(os.environ.get('TTS_OUTPUT_DIR', str(Path.cwd() / 'tts-output'))).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / f'{digest}.{format}'
    cached = output.exists()
    if cached:
        try:
            audio_info(output, format)
        except (ValueError, wave.Error, EOFError):
            output.unlink()
            cached = False
    if not cached:
        fd, name = tempfile.mkstemp(dir=directory, suffix='.' + format)
        os.close(fd)
        temporary = Path(name)
        try:
            with contextlib.redirect_stdout(sys.stderr):
                render(provider, text, voice, speed, format, temporary)
            audio_info(temporary, format)
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
    info = audio_info(output, format)
    return {'path': str(output), 'provider': provider, 'requestedProvider': provider, 'actualProvider': provider, 'fallbackReason': None, 'format': format, 'mimeType': MIME[format],
            'offline': provider in OFFLINE, 'cached': cached, 'bytes': output.stat().st_size,
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(), **info}


def voices(provider):
    if provider == 'youdao':
        return [{'id': 'en-US', 'type': 2}, {'id': 'en-GB', 'type': 1}]
    if provider == 'macos':
        if sys.platform != 'darwin':
            raise ValueError('macos voice listing requires macOS.')
        result = subprocess.run(['say', '-v', '?'], capture_output=True, timeout=15)
        if result.returncode:
            raise ValueError('macOS voice listing failed.')
        return {'installedVoices': result.stdout.decode('utf-8')}
    if provider == 'edge':
        import asyncio
        async def fetch():
            try:
                import edge_tts
                return await asyncio.wait_for(edge_tts.list_voices(proxy=os.environ.get('TTS_EDGE_PROXY') or None), 30)
            except Exception:
                raise ValueError('Edge voice listing failed; check dependency, network and proxy.') from None
        return asyncio.run(fetch())
    if provider == 'windows':
        return windows_call({'action': 'voices'})
    if provider == 'azure':
        region = required('AZURE_SPEECH_REGION')
        if not re.fullmatch(r'[a-z0-9-]+', region):
            raise ValueError('Invalid Azure Speech region.')
        return json.loads(request(f'https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list',
                                 {'Ocp-Apim-Subscription-Key': required('AZURE_SPEECH_KEY')}))
    if provider == 'elevenlabs':
        return json.loads(request('https://api.elevenlabs.io/v2/voices?page_size=100',
                                 {'xi-api-key': required('ELEVENLABS_API_KEY')}))
    raise ValueError('Use the sherpa model speaker IDs or your Speech API provider voice documentation.')


def doctor():
    requirements = {'windows': [], 'macos': [], 'sherpa': ['TTS_SHERPA_CONFIG'], 'edge': [], 'youdao': [],
        'dashscope': ['DASHSCOPE_API_KEY', 'TTS_DASHSCOPE_MODEL', 'TTS_DASHSCOPE_VOICE'],
        'azure': ['AZURE_SPEECH_KEY', 'AZURE_SPEECH_REGION'],
        'elevenlabs': ['ELEVENLABS_API_KEY', 'ELEVENLABS_MODEL_ID', 'ELEVENLABS_VOICE_ID'],
        'speech-api': ['TTS_SPEECH_API_KEY', 'TTS_SPEECH_URL', 'TTS_SPEECH_MODEL', 'TTS_SPEECH_VOICE']}
    providers = {}
    for provider in PROVIDERS:
        dependencies = True
        if provider in {'sherpa', 'edge'}:
            dependencies = importlib.util.find_spec('sherpa_onnx' if provider == 'sherpa' else 'edge_tts') is not None
        supported = sys.platform == 'win32' if provider == 'windows' else sys.platform == 'darwin' if provider == 'macos' else True
        missing = [key for key in requirements[provider] if not os.environ.get(key)]
        providers[provider] = {'offline': provider in OFFLINE, 'formats': FORMATS[provider],
            'platformSupported': supported, 'dependencyInstalled': dependencies, 'missingConfiguration': missing,
            'configurationPresent': not missing, 'networkChecked': False, 'modelLoaded': False}
    if os.environ.get('TTS_SHERPA_CONFIG'):
        try:
            sherpa_config()
            providers['sherpa']['modelPathsValid'] = True
        except Exception:
            providers['sherpa']['modelPathsValid'] = False
    return {'version': VERSION, 'python': sys.version.split()[0], 'pythonExecutable': sys.executable, 'platform': sys.platform,
        'outputDirectory': str(Path(os.environ.get('TTS_OUTPUT_DIR', 'tts-output')).resolve()),
        'mp3DecoderAvailable': bool(ffmpeg_path()), 'providers': providers,
        'note': 'No network calls or credentials returned. This is a readiness inspection, not a synthesis test.'}


def split_text(text, limit):
    if not isinstance(text, str) or not text.strip() or len(text) > 100000:
        raise ValueError('Batch text must contain 1–100000 characters.')
    chunks, current = [], ''
    for sentence in re.findall(r'.+?(?:[.!?。！？\n]+|$)', text, re.DOTALL):
        while sentence:
            room = limit - len(current)
            current += sentence[:room]
            sentence = sentence[room:]
            if len(current) == limit:
                chunks.append(current)
                current = ''
        if current and len(current) >= limit // 2:
            chunks.append(current)
            current = ''
    if current:
        chunks.append(current)
    return chunks


def synthesize_batch(provider, text, voice='', speed=1.0, format='wav', offline_only=True):
    if provider == 'youdao':
        raise ValueError('Use individual Youdao word/phrase lookups; batch paragraphs are unsupported.')
    if provider not in PROVIDERS or (offline_only and provider not in OFFLINE):
        raise ValueError('Invalid provider or offline_only blocks online batch synthesis.')
    clips = split_text(text, 600 if provider == 'dashscope' else 2500)
    results = []
    for index, clip in enumerate(clips):
        if not clip.strip():
            continue
        try:
            results.append(synthesize(provider, clip, voice, speed, format, offline_only))
        except Exception:
            raise ValueError(f'Batch stopped at clip {index + 1}/{len(clips)}. Completed clips remain cached; rerun the same request to resume. No provider switch or automatic retry.') from None
    playlist = {'version': VERSION, 'provider': provider, 'clips': results, 'count': len(results)}
    directory = Path(os.environ.get('TTS_OUTPUT_DIR', str(Path.cwd() / 'tts-output'))).expanduser().resolve()
    name = hashlib.sha256(json.dumps([r['path'] for r in results]).encode()).hexdigest() + '.playlist.json'
    path = directory / name
    path.write_text(json.dumps(playlist, ensure_ascii=False, indent=2), encoding='utf-8')
    return {**playlist, 'playlistPath': str(path)}


TOOLS = [
    {'name': 'tts_doctor', 'description': 'Check local runtime and configuration presence without networking or revealing credentials.', 'inputSchema': {'type': 'object', 'properties': {}, 'additionalProperties': False}},
    {'name': 'tts_catalog', 'description': 'Read the sourced online/offline TTS shortlist. Catalog entries are not all implemented adapters.', 'inputSchema': {'type': 'object', 'properties': {}, 'additionalProperties': False}},
    {'name': 'tts_voices', 'description': 'List local voices, static Youdao accents, or fetch cloud voices. Edge/Azure/ElevenLabs require networking.', 'inputSchema': {'type': 'object', 'properties': {'provider': {'type': 'string', 'enum': ['macos', 'windows', 'youdao', 'edge', 'azure', 'elevenlabs']}}, 'required': ['provider'], 'additionalProperties': False}},
    {'name': 'tts_synthesize', 'description': 'Generate and cache a local audio file. Cloud requests may incur cost and send text externally; require offline_only=false. Never automatically switches providers or retries.', 'inputSchema': {'type': 'object', 'properties': {
        'provider': {'type': 'string', 'enum': PROVIDERS}, 'text': {'type': 'string', 'minLength': 1, 'maxLength': 3000},
        'voice': {'type': 'string'}, 'speed': {'type': 'number', 'minimum': 0.5, 'maximum': 2, 'default': 1},
        'format': {'type': 'string', 'enum': ['wav', 'mp3'], 'default': 'wav'},
        'offline_only': {'type': 'boolean', 'default': True}}, 'required': ['provider', 'text'], 'additionalProperties': False}}
]
BATCH_TOOL = json.loads(json.dumps(TOOLS[-1]))
BATCH_TOOL['name'] = 'tts_synthesize_batch'
BATCH_TOOL['description'] = 'Split long text, generate cached clips and a playlist. Stops on failure; rerunning resumes from cached clips. Online requests require offline_only=false and may incur per-clip charges.'
BATCH_TOOL['inputSchema']['properties']['text']['maxLength'] = 100000
TOOLS.append(BATCH_TOOL)


def call_tool(name, arguments):
    if name == 'tts_doctor':
        return doctor()
    if name == 'tts_catalog':
        return json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
    if name == 'tts_voices':
        return voices(**arguments)
    if name == 'tts_synthesize':
        return synthesize(**arguments)
    if name == 'tts_synthesize_batch':
        return synthesize_batch(**arguments)
    raise ValueError('Unknown tool.')


def dispatch(message):
    if not isinstance(message, dict):
        return {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32600, 'message': 'Invalid request'}}
    if 'id' not in message:
        return None
    method, params = message.get('method'), message.get('params', {})
    response = {'jsonrpc': '2.0', 'id': message['id']}
    if not isinstance(params, dict):
        response['error'] = {'code': -32602, 'message': 'params must be an object'}
        return response
    if method == 'initialize':
        versions = ['2024-11-05', '2025-03-26', '2025-06-18']
        version = params.get('protocolVersion')
        response['result'] = {'protocolVersion': version if version in versions else versions[-1],
                              'capabilities': {'tools': {'listChanged': False}},
                              'serverInfo': {'name': 'tts-studio', 'version': VERSION}}
    elif method == 'ping':
        response['result'] = {}
    elif method == 'tools/list':
        response['result'] = {'tools': TOOLS}
    elif method == 'tools/call':
        try:
            name, arguments = params['name'], params.get('arguments', {})
            schema = next((t['inputSchema'] for t in TOOLS if t['name'] == name), None)
            if schema is None or not isinstance(arguments, dict) or set(arguments) - set(schema['properties']) or set(schema.get('required', [])) - set(arguments):
                raise ValueError('Unknown tool or invalid arguments.')
            result = call_tool(name, arguments)
            response['result'] = {'content': [{'type': 'text', 'text': json.dumps(result, ensure_ascii=False)}], 'isError': False}
        except Exception as error:
            safe = str(error) if isinstance(error, ValueError) else f'{type(error).__name__}: tool failed; check local configuration.'
            response['result'] = {'content': [{'type': 'text', 'text': safe}], 'isError': True}
    else:
        response['error'] = {'code': -32601, 'message': 'Method not found'}
    return response


def main():
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser()
        parser.add_argument('action', choices=['doctor', 'voices', 'synthesize', 'batch', 'catalog'])
        parser.add_argument('--provider', choices=PROVIDERS)
        parser.add_argument('--text')
        parser.add_argument('--voice', default='')
        parser.add_argument('--format', choices=['wav', 'mp3'], default='wav')
        parser.add_argument('--speed', type=float, default=1)
        parser.add_argument('--allow-online', action='store_true')
        args = parser.parse_args()
        try:
            if args.action in {'synthesize', 'batch', 'voices'} and not args.provider:
                raise ValueError('Select --provider explicitly; use doctor to inspect available engines.')
            result = (synthesize if args.action == 'synthesize' else synthesize_batch)(args.provider, args.text, args.voice, args.speed, args.format, not args.allow_online) if args.action in {'synthesize', 'batch'} else voices(args.provider) if args.action == 'voices' else call_tool('tts_' + args.action, {})
            print(json.dumps(result, ensure_ascii=True, indent=2))
        except Exception as error:
            print(str(error) if isinstance(error, ValueError) else type(error).__name__ + ': check local configuration', file=sys.stderr)
            sys.exit(1)
        return
    for line in sys.stdin.buffer:
        try:
            message = json.loads(line)
            result = dispatch(message)
        except Exception:
            result = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': 'Parse error'}}
        if result is not None:
            sys.stdout.buffer.write((json.dumps(result, ensure_ascii=True) + '\n').encode('utf-8'))
            sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
