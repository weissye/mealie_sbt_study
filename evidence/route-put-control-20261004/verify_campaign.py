"""Read-only checksum and failed-control qualification checks."""
import hashlib,io,json,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
for name,digest in json.loads((HERE/'checksums.json').read_text()).items():
 if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=digest:raise ValueError('Evidence checksum mismatch: '+name)
def read(z,name):
 matches=[n for n in z.namelist() if n.replace(chr(92),'/')==name]
 if len(matches)!=1:raise ValueError('Missing or ambiguous ZIP member: '+name)
 return z.read(matches[0])
with zipfile.ZipFile(HERE/'campaign-original.zip') as z:
 result=json.loads(read(z,'control/result-1.json'));payload=read(z,'control/live-1.zip')
 if hashlib.sha256(payload).hexdigest()!=result['sha256']:raise ValueError('Live archive checksum mismatch')
 with zipfile.ZipFile(io.BytesIO(payload)) as live:
  acceptance=json.loads(read(live,'execution-review/run-acceptance.json'))
  if acceptance['live_accepted'] or acceptance['native_exit_code']!=1 or 'updated_target_identity_or_state' not in acceptance['error']:raise ValueError('Expected failed control was not preserved')
print('ROUTE_PUT_CONTROL_EVIDENCE_VERIFIED: preserved failed control and pinned source; no new bug confirmed. No HTTP requests sent.')
