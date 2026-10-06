"""Read-only normalized text and raw binary release checksum verification."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
release=json.loads((root/'validation/mealie-native-distinct-merge-release.json').read_text(encoding='utf-8-sig'))
for name,record in release['files'].items():
    path=root/name
    assert path.is_file(),'Missing release file: '+name
    data=path.read_bytes()
    if record['normalization']=='LF':data=data.replace(b'\r\n',b'\n')
    assert hashlib.sha256(data).hexdigest()==record['sha256'],'Release checksum differs: '+name
print('NATIVE_DISTINCT_MERGE_RELEASE_VERIFIED. No API requests sent.')
