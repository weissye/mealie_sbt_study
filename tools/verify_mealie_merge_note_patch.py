"""Read-only checksums for the repair delta (not the existing installation)."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
report=json.loads((root/'validation/mealie-merge-note-fix-validation.json').read_text(encoding='utf-8-sig'))
for name,record in report['files'].items():
    raw=(root/name).read_bytes()
    if record['normalization']=='LF':raw=raw.replace(b'\r\n',b'\n')
    assert hashlib.sha256(raw).hexdigest()==record['sha256'],'Repair file checksum differs: '+name
print('MERGE_NOTE_FIX_DELTA_VERIFIED. No API requests sent.')
