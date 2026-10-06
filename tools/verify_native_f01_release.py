import hashlib,json,sys
from pathlib import Path
root=Path(sys.argv[1]);manifest=json.loads((root/'validation/native-f01-release.json').read_text(encoding='utf-8-sig'))
for record in manifest['files']:
    p=root/record['path']
    if not p.is_file():raise SystemExit('Missing release file: '+str(p))
    b=p.read_bytes().replace(b'\r\n',b'\n')
    if hashlib.sha256(b).hexdigest()!=record['sha256_lf']:raise SystemExit('Release content mismatch: '+record['path'])
print('NATIVE_F01_RELEASE_VERIFIED. No API requests sent.')
