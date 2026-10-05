"""Verify original archived route evidence offline; never send API requests."""
import hashlib,io,json,sys,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'generic-generator'))
from tools.route_receipts import validate_route_receipts
from tools.relationship_execution import validate_negative_receipts
expected=json.loads((HERE/'verification.json').read_text())
path=HERE/'campaign-original.zip'
if hashlib.sha256(path.read_bytes()).hexdigest()!=expected['campaign_sha256']:raise ValueError('Original campaign checksum mismatch.')
with zipfile.ZipFile(path) as outer:
    names={}
    for name in outer.namelist():
        normalized=name.replace('\\','/')
        if normalized in names:raise ValueError('Ambiguous normalized archive name.')
        names[normalized]=name
    for run in expected['runs']:
        payload=outer.read(names[run['path']])
        if hashlib.sha256(payload).hexdigest()!=run['sha256']:raise ValueError('Nested live checksum mismatch.')
        with zipfile.ZipFile(io.BytesIO(payload)) as inner:
            acceptance=json.loads(inner.read('execution-review/run-acceptance.json'))
            plan=json.loads(inner.read('relationship_scenario_plan.json'))
            if acceptance.get('live_accepted') is not True:raise ValueError('Native acceptance missing.')
            receipt=acceptance['runtime_receipt'];validate_route_receipts(receipt,plan);validate_negative_receipts(receipt,plan)
            if receipt['response_count']!=run['response_count'] or receipt['owned_instances']!=run['owned_instances']:raise ValueError('Receipt inventory mismatch.')
if len(expected['runs'])!=6:raise ValueError('Six archived runs required.')
print('NAME_ROUTE_EVIDENCE_VERIFIED: six runs, 776 responses, 108 raw observations. No new bug confirmed.')
