import json
from pathlib import Path

root = Path(__file__).parent / 'tts-studio'
for name in ['plugin.json', '.codex-plugin/plugin.json']:
    path = root / name
    data = json.loads(path.read_text(encoding='utf-8'))
    data['version'] = '0.2.0'
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
for name in ['mcp.json', '.mcp.json']:
    path = root / name
    data = json.loads(path.read_text(encoding='utf-8'))
    data['mcpServers']['tts-studio']['command'] = 'python3'
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
path = root / 'catalog.json'
data = json.loads(path.read_text(encoding='utf-8'))
for entry in data['offline']:
    if entry['name'].startswith('System speech'):
        entry['status'] = 'Windows SAPI and macOS say adapters implemented; macOS requires target-device verification'
for entry in data['online']:
    if entry['name'].startswith('Alibaba'):
        entry['status'] = 'dashscope adapter implements Qwen-TTS non-realtime Beijing/Singapore WAV output; hosted CosyVoice is still a candidate'
for name, use, status, url in [
    ('Edge TTS', 'Preferred online reading and cached MP3 generation across macOS/Linux/Windows', 'Implemented with explicit proxy and timeout; network availability is not guaranteed', 'https://github.com/rany2/edge-tts'),
    ('Youdao dictionary voice', 'English word and short-phrase pronunciation and audio saving', 'Implemented with HTTPS, encoded query and US/UK accents; not arbitrary-text TTS; no paid API credentials', 'https://dict.youdao.com/')]:
    if not any(e['name'] == name for e in data['online']):
        data['online'].append({'name': name, 'use': use, 'status': status, 'source': url})
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
