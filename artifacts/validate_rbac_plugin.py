import json
import re
import zipfile
from pathlib import Path
import yaml

base = Path(__file__).resolve().parent
root = base / 'rbac-builder-0.4.0'
old = json.loads((base / 'rbac-builder-0.3.1-source-backup.json').read_text(encoding='utf-8'))
manifest = json.loads((root / 'plugin.json').read_text(encoding='utf-8'))
overlay = json.loads((root / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
assert manifest['$schema'] == 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json'
for path, current in [('plugin.json', manifest), ('.codex-plugin/plugin.json', overlay)]:
    previous = json.loads(old[path])
    assert current['name'] == previous['name'] == 'rbac-builder'
    assert current['version'] == '0.4.0'
    expected = json.loads(old[path])
    expected['version'] = '0.4.0'
    old_ui = previous['extensions']['com.openai']['interface'] if path == 'plugin.json' else previous['interface']
    new_ui = current['extensions']['com.openai']['interface'] if path == 'plugin.json' else current['interface']
    expected_ui = expected['extensions']['com.openai']['interface'] if path == 'plugin.json' else expected['interface']
    expected_ui['longDescription'] = new_ui['longDescription']
    assert current == expected, 'Unexpected metadata change: ' + path
    assert old_ui['defaultPrompt'] == new_ui['defaultPrompt']
    assert len(new_ui['shortDescription']) <= 30
    assert new_ui['displayName'] == 'RBAC Builder'
skill = root / 'skills/build-rbac/SKILL.md'
text = skill.read_text(encoding='utf-8')
header = yaml.safe_load(text.split('---', 2)[1])
assert header['name'] == 'build-rbac' and header['description'].strip()
refs = re.findall(r'references/[a-z-]+\.md', text)
assert len(set(refs)) == 6
for ref in refs:
    assert (skill.parent / ref).is_file(), ref
removed = ['frontend-design.md', 'application-foundation.md']
all_text = '\n'.join(p.read_text(encoding='utf-8') for p in root.rglob('*') if p.is_file())
for name in removed:
    assert name not in all_text
assert len(list(root.rglob('SKILL.md'))) == 1
archive = base / 'rbac-builder-0.4.0.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as out:
    for path in sorted(root.rglob('*')):
        if path.is_file():
            assert not path.is_symlink()
            out.write(path, path.relative_to(root).as_posix())
with zipfile.ZipFile(archive) as package:
    assert package.testzip() is None
    assert len(package.namelist()) == 9
    assert 'plugin.json' in package.namelist()
report = {
    'version': '0.4.0',
    'structural_checks': 'passed',
    'metadata_preservation': 'passed; only version and longDescription changed',
    'references': len(set(refs)),
    'archive_files': 9,
    'deletions': ['skills/build-rbac/references/' + name for name in removed],
    'live_behavior_evaluations': 'not run: no host evaluation harness configured',
    'archive': str(archive),
}
(base / 'rbac-builder-0.4.0-validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
