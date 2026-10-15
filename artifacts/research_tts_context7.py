import concurrent.futures
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request

OUT = Path(__file__).parent / 'tts-studio' / 'research'
QUERIES = {
    'sherpa-onnx': 'offline Chinese English TTS Python OfflineTtsConfig generate save wav WebAssembly',
    'kokoro': 'Kokoro TTS languages Chinese English model license browser kokoro-js',
    'piper': 'Piper text to speech local voices license Python API',
    'Qwen3-TTS': 'Qwen3 TTS languages local inference license hardware',
    'CosyVoice': 'CosyVoice multilingual Chinese streaming local deployment license',
    'F5-TTS': 'F5 TTS pretrained model license commercial inference Chinese English',
    'ElevenLabs': 'text to speech REST POST /v1/text-to-speech voice_id output_format headers',
    'Azure Speech': 'text to speech REST cognitiveservices v1 SSML subscription key output format',
    'Google Cloud text to speech': 'text to speech synthesize voices Chirp audioEncoding',
    'Amazon Polly': 'synthesize speech neural generative voices languages',
    'DashScope Qwen TTS': 'Qwen TTS speech synthesis API streaming languages',
    'saritasa speech synthesis': 'Web Speech API speechSynthesis browser localService export audio',
}

def get(path, params):
    headers = {}
    if os.environ.get('CONTEXT7_API_KEY'):
        headers['Authorization'] = 'Bearer ' + os.environ['CONTEXT7_API_KEY']
    url = 'https://context7.com/api/v2/' + path + '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=40) as r:
        return r.read().decode('utf-8')

def collect(item):
    name, query = item
    try:
        search = json.loads(get('libs/search', {'libraryName': name, 'query': query}))
        results = search.get('results', [])
        result = {'name': name, 'query': query, 'search': search}
        if results:
            result['libraryId'] = results[0]['id']
            result['context'] = get('context', {'libraryId': results[0]['id'], 'query': query, 'type': 'txt'})
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / (name.replace(' ', '-') + '.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        return {'name': name, 'library': result.get('libraryId'), 'context': result.get('context', '')[:11000]}
    except Exception as e:
        return {'name': name, 'error': str(e)}

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(collect, QUERIES.items()):
            print(json.dumps(result, ensure_ascii=False), flush=True)
