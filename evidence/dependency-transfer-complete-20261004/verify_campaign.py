"""Offline complete campaign verification; never sends HTTP."""
import hashlib,io,json,sys,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'generic-generator'))
from tools.transfer_receipts import validate_transfer_receipts
from tools.reference_receipts import validate_reference_receipts

def read(z,path):
 names=[n for n in z.namelist() if n.replace(chr(92),'/')==path]
 if len(names)!=1:raise ValueError('Missing or ambiguous ZIP member: '+path)
 return z.read(names[0])
for path,digest in json.loads((HERE/'checksums.json').read_text()).items():
 if hashlib.sha256((HERE/path).read_bytes()).hexdigest()!=digest:raise ValueError('Original archive checksum mismatch.')
total=0;identities=set();seen=set()
with zipfile.ZipFile(HERE/'campaign-original.zip') as campaign:
 summary=json.loads(read(campaign,'campaign-summary.json').decode('utf-8-sig'))
 if len(summary['runs'])!=8:raise ValueError('Expected eight completed runs.')
 for run in summary['runs']:
  case=run['case'];sample=run['sample'];key=(case,sample)
  if key in seen:raise ValueError('Duplicate run.')
  seen.add(key);result=json.loads(read(campaign,case+'/result-'+str(sample)+'.json'));payload=read(campaign,case+'/live-'+str(sample)+'.zip')
  if hashlib.sha256(payload).hexdigest()!=result['sha256']:raise ValueError('Nested live archive checksum mismatch.')
  with zipfile.ZipFile(io.BytesIO(payload)) as live:
   acceptance=json.loads(read(live,'execution-review/run-acceptance.json').decode('utf-8-sig'));plan=json.loads(read(live,'relationship_scenario_plan.json'));comp=json.loads(read(live,'relationship_compilation.json'))
   if acceptance.get('live_accepted') is not True or run['native_exit']!=0 or result['status']!='PASS':raise ValueError('Incomplete live acceptance.')
   receipt=acceptance['runtime_receipt'];validate_transfer_receipts(receipt,plan);validate_reference_receipts(receipt,plan)
   if receipt['response_count']!=comp['http_requests_per_complete_schedule']:raise ValueError('Response count mismatch.')
   ids={o['route']['id'] for o in receipt['owned_records']}
   if identities.intersection(ids):raise ValueError('Resources reused between runs.')
   identities.update(ids);total+=receipt['response_count']
 if seen!={(case,sample) for case in ['food-control','unit-control','food-transfer','unit-transfer'] for sample in [1,2]} or total!=1108 or len(identities)!=96:raise ValueError('Campaign coverage mismatch.')
print('DEPENDENCY_TRANSFER_EVIDENCE_VERIFIED: eight live runs, 1108 responses, 96 distinct owned UUIDs. No new bug confirmed. No HTTP requests sent.')
