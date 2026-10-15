"""Prepare a reusable personal marketplace. Does not edit host config or install dependencies."""
import argparse
import json
from pathlib import Path
import shutil
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--destination', type=Path, default=Path.home() / '.local/share/tts-studio-marketplace')
parser.add_argument('--python', default=sys.executable, help='Absolute path to the Python environment containing dependencies')
args = parser.parse_args()
source = Path(__file__).resolve().parents[1]
destination = args.destination.expanduser().resolve()
if destination == source or source in destination.parents:
    parser.error('Destination must be outside the source plugin directory.')
interpreter = Path(args.python).expanduser().resolve()
if not interpreter.is_file():
    parser.error('--python must point to an existing Python executable.')
target = destination / 'plugins/tts-studio'
if target == source:
    parser.error('Source is already in this marketplace; update its configuration directly or choose another destination.')
catalog = destination / '.agents/plugins/marketplace.json'
data = json.loads(catalog.read_text(encoding='utf-8')) if catalog.exists() else {'name': 'tts-studio-local', 'plugins': []}
if data.get('name') != 'tts-studio-local':
    parser.error('Destination already contains a different marketplace; choose a separate destination.')
shutil.copytree(source, target, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '.venv', 'tts-output'))
for name in ['mcp.json', '.mcp.json']:
    path = target / name
    config = json.loads(path.read_text(encoding='utf-8'))
    server = config['mcpServers']['tts-studio']
    server['command'] = str(interpreter)
    server['args'] = [str(target / 'server/tts_server.py')]
    server['cwd'] = str(target)
    path.write_text(json.dumps(config, indent=2), encoding='utf-8')
catalog.parent.mkdir(parents=True, exist_ok=True)
entry = {'name': 'tts-studio', 'source': {'source': 'local', 'path': './plugins/tts-studio'},
         'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, 'category': 'Productivity'}
data['plugins'] = [p for p in data.get('plugins', []) if p.get('name') != 'tts-studio'] + [entry]
catalog.write_text(json.dumps(data, indent=2), encoding='utf-8')
print(json.dumps({'marketplace': str(destination), 'python': str(interpreter),
                  'nextCommands': [f'codex plugin marketplace add "{destination}"',
                                   'codex plugin add tts-studio@tts-studio-local'],
                  'note': 'Run commands in a supporting local client, then refresh/restart the host. No global configuration was edited.'}, indent=2))
