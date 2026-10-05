"""Offline verification of preserved evidence; no server access."""
import ast, hashlib, io, json, zipfile
from pathlib import Path
from qualification_oracle import IdentityMismatch, validate_identity_receipts
root=Path(__file__).resolve().parent
for name, expected in json.loads((root/'checksums.json').read_text()).items():
    assert Path(name).name==name
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected, name
qualified=json.loads((root/'qualification.json').read_text())
seen=set(); total=0
with zipfile.ZipFile(root/'campaign-original.zip') as campaign:
    assert campaign.testzip() is None
    summary=json.loads(campaign.read('campaign-summary.json'))
    assert {(x['case'],x['sample']) for x in summary['runs']}=={('reference-controls',1),('reference-controls',2),('household-controls',1),('household-controls',2)}
    for run in summary['runs']:
        payload=campaign.read(f"{run['case']}/live-{run['sample']}.zip")
        assert hashlib.sha256(payload).hexdigest()==run['sha256']
        with zipfile.ZipFile(io.BytesIO(payload)) as live:
            assert live.testzip() is None
            result=json.loads(live.read('run-acceptance.json'))
            plan=json.loads(live.read('relationship_scenario_plan.json'))
            receipt=result['runtime_receipt']; ip=receipt['identity_program']; obs=ip['observations']
            assert result['native_exit']==0 and receipt['status']=='LIVE_CALLBACKS_COMPLETE'
            assert ip['namespace'] not in seen; seen.add(ip['namespace'])
            assert len(obs)==(47 if run['case']=='reference-controls' else 46)
            total+=len(obs); issues=[]
            try: validate_identity_receipts(receipt,plan)
            except IdentityMismatch as exc: issues=ast.literal_eval(str(exc))
            recorded=next(x for x in qualified['runs'] if x['case']==run['case'] and x['sample']==run['sample'])
            assert issues==recorded['independent_issues'] and len(issues)==4
            assert recorded['live_sha256']==run['sha256']
            if run['case']=='household-controls':
                for before,after in [('cross_list_b','owner_list_after_a'),('cross_list_a','owner_list_after_b')]:
                    x={v['id']:v for v in obs[before]['body']['listItems']}
                    y={v['id']:v for v in obs[after]['body']['listItems']}
                    assert len(x)==2 and len(y)==3 and len(y.keys()-x.keys())==1
                    assert all(y[k]==v for k,v in x.items())
assert total==186 and qualified['total_responses']==total
print('SCOPE_CONTROLS_EVIDENCE_VERIFIED: four complete runs; 186 responses; original error reproduced; four substantive household list changes. No API calls sent.')
