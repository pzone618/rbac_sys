"""Dependency-free actual-process smoke test for macOS/Linux/Windows."""
import json
from pathlib import Path
import subprocess
import sys

server = Path(__file__).resolve().parents[1] / 'server/tts_server.py'
messages = [
    {'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2025-06-18'}},
    {'method': 'notifications/initialized'},
    {'id': 2, 'method': 'tools/list'},
    {'id': 3, 'method': 'tools/call', 'params': {'name': 'tts_doctor', 'arguments': {}}},
    {'id': 4, 'method': 'tools/call', 'params': {'name': 'tts_catalog', 'arguments': {}}},
    {'id': 5, 'method': 'initialize', 'params': []},
    {'id': 6, 'method': 'tools/call', 'params': {'name': 'tts_synthesize', 'arguments': {'provider': 'edge', 'text': 'Private', 'format': 'mp3'}}}
]
process = subprocess.run([sys.executable, str(server)], input=''.join(json.dumps({'jsonrpc': '2.0', **m}) + '\n' for m in messages), capture_output=True, text=True, timeout=30)
assert process.returncode == 0, process.stderr
results = [json.loads(line) for line in process.stdout.splitlines()]
assert len(results) == 6
assert results[0]['result']['serverInfo']['version'] == '0.2.0'
assert len(results[1]['result']['tools']) == 5
doctor = json.loads(results[2]['result']['content'][0]['text'])
assert doctor['platform'] == sys.platform
assert not results[3]['result']['isError']
assert results[4]['error']['code'] == -32602
assert results[5]['result']['isError']
assert 'offline_only' in results[5]['result']['content'][0]['text']
if sys.platform == 'linux':
    assert not doctor['providers']['windows']['platformSupported']
    assert not doctor['providers']['macos']['platformSupported']
print(json.dumps({'platform': sys.platform, 'version': '0.2.0', 'smoke': 'passed', 'tools': 5}))
