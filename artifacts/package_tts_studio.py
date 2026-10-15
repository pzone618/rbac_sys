"""Build and inspect the private TTS Studio archive without runtime data."""
import json
from pathlib import Path
import zipfile

BASE = Path(__file__).resolve().parent
ROOT = BASE / 'tts-studio'
VERSION = json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8'))['version']
OUTPUT = BASE / f'tts-studio-{VERSION}.zip'
EXCLUDE = {'__pycache__', 'node_modules', 'tts-output', '.venv'}

for file in ROOT.rglob('*.json'):
    json.loads(file.read_text(encoding='utf-8'))
manifest = json.loads((ROOT / 'plugin.json').read_text(encoding='utf-8'))
legacy = json.loads((ROOT / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
assert manifest['$schema'] == 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
assert manifest['name'] == legacy['name'] == ROOT.name
assert manifest['version'] == legacy['version'] == VERSION
assert len(manifest['extensions']['com.openai']['interface']['shortDescription']) <= 30
for f in ROOT.rglob('SKILL.md'):
    assert f.read_text(encoding='utf-8').startswith('---\nname:')

with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(ROOT.rglob('*')):
        if file.is_file() and not EXCLUDE.intersection(file.relative_to(ROOT).parts):
            assert not file.is_symlink()
            archive.write(file, file.relative_to(ROOT).as_posix())
with zipfile.ZipFile(OUTPUT) as archive:
    assert archive.testzip() is None
    names = archive.namelist()
    for required in ['plugin.json', 'mcp.json', '.mcp.json', '.codex-plugin/plugin.json', 'server/tts_server.py', 'catalog.json', 'skills/website-tts/SKILL.md']:
        assert required in names, required
    assert not any(n.endswith(('.wav', '.mp3', '.pyc', '.env')) for n in names)
    print(json.dumps({'archive': str(OUTPUT), 'files': len(names), 'bytes': OUTPUT.stat().st_size, 'validated': True}))
