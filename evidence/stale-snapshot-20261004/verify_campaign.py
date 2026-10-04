"""Verify preserved stale-snapshot evidence offline. No API requests."""
import hashlib,io,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'generic-generator'))
from tools.reference_receipts import validate_reference_receipts
def read_member(archive,name):
 def canonical(value):return '/'.join(part for part in value.replace(chr(92),'/').split('/') if part)
 wanted=canonical(name)
 matches=[member for member in archive.namelist() if canonical(member)==wanted]
 if len(matches)!=1:raise ValueError('Archive member missing or ambiguous: '+wanted)
 return archive.read(matches[0])

HERE=Path(__file__).resolve().parent
manifest=json.loads((HERE/'checksums.json').read_text())
for name,digest in manifest.items():
 if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=digest:raise ValueError('Evidence checksum mismatch: '+name)
with zipfile.ZipFile(HERE/'campaign-original.zip') as campaign:
 summary=json.loads(read_member(campaign,'campaign-summary.json').decode('utf-8-sig'));assert len(summary['runs'])==8
 for item in summary['runs']:
  name=item['case']+'/result-'+str(item['sample'])+'.json'
  result=json.loads(read_member(campaign,name));live=name.replace('result','live').replace('.json','.zip');payload=read_member(campaign,live)
  assert hashlib.sha256(payload).hexdigest()==result['sha256']
  with zipfile.ZipFile(io.BytesIO(payload)) as archive:
   acceptance=json.loads(read_member(archive,'execution-review/run-acceptance.json').decode('utf-8-sig'));plan=json.loads(read_member(archive,'relationship_scenario_plan.json'))
   if item['case'].endswith('-control'):
    assert result['status']=='PASS' and acceptance['live_accepted'] is True
    validate_reference_receipts(acceptance['runtime_receipt'],plan)
   else:
    assert result['status']=='POLICY_OBSERVATION'
    evidence=result['first_failure'];assert evidence['stage']=='stale_success_requires_policy_qualification'
    stale=evidence['observed'];assert stale['code']==200 and stale['accepted'] is True and stale['target_read']=={'code':404,'observed':None}
    assert len(stale['checks'])==6 and all(c['expected']==c['observed'] for c in stale['checks'])
    source=next(c for c in stale['checks'] if c['instance']=='api/recipes#1');assert source['field_value']==stale['value']
print('STALE_EVIDENCE_VERIFIED: four complete controls; four consistent deletion-policy observations. No new bug confirmed. No API requests sent.')
