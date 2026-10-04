"""Offline preservation and native receipt verification; no server requests."""
from pathlib import Path
import hashlib,io,json,sys,zipfile
folder=Path(__file__).resolve().parent
root=folder.parents[1]
sys.path.insert(0,str(root/'generic-generator'))
from tools.reference_receipts import validate_reference_receipts
checks=json.loads((folder/'original-sha256.json').read_text(encoding='utf-8-sig'))
for name,wanted in checks.items():
    path=folder/name
    if hashlib.sha256(path.read_bytes()).hexdigest()!=wanted:raise ValueError('Original evidence checksum mismatch: '+name)
seen=set();orders={};responses=0;count=0;deletions=0
with zipfile.ZipFile(folder/'accepted-campaign.zip') as outer:
    for name in outer.namelist():
        normalized=name.replace('\\','/')
        if '/live-' not in normalized or not normalized.endswith('.zip'):continue
        case=normalized.split('/')[0]
        with zipfile.ZipFile(io.BytesIO(outer.read(name))) as archive:
            acceptance=json.loads(archive.read('execution-review/run-acceptance.json').decode('utf-8-sig'))
            plan=json.loads(archive.read('relationship_scenario_plan.json').decode('utf-8-sig'))
            compilation=json.loads(archive.read('relationship_compilation.json').decode('utf-8-sig'))
            receipt=acceptance.get('runtime_receipt',{})
            if acceptance.get('live_accepted') is not True or acceptance.get('native_exit_code')!=0:raise ValueError('Run is not accepted.')
            validate_reference_receipts(receipt,plan)
            if receipt['task_count']!=len(plan['tasks']) or receipt['response_count']!=compilation['http_requests_per_complete_schedule']:raise ValueError('Incomplete callback coverage.')
            ids={o['route']['id'] for o in receipt['owned_records']}
            if len(ids)!=12 or seen&ids:raise ValueError('Resources are not disjoint.')
            seen|=ids;responses+=receipt['response_count'];count+=1
            lifecycle=receipt['reference_lifecycles'][0]
            if case.endswith('-delete'):
                if not lifecycle['deleted'] or lifecycle['delete_code']!=200 or [r['code'] for r in lifecycle['target_reads']]!=[404,404]:raise ValueError('Unexpected deletion outcome.')
                deletions+=1
            elif lifecycle['outcome']!='CONTROL_NO_DELETE':raise ValueError('Wrong control outcome.')
            output=archive.read('execution-review/run-output.txt').decode('utf-8-sig')
            if 'Test Result: SUCCESS' not in output:raise ValueError('Native result was not success.')
            order=tuple(line.split('Selected: ',1)[1] for line in output.splitlines() if 'Selected: [SBT:RelTask ' in line)
            if len(order)!=25:raise ValueError('Incomplete selected task order.')
            orders.setdefault(case,[]).append(order)
if count!=8 or responses!=804 or len(seen)!=96 or deletions!=4 or len(orders)!=4 or any(len(v)!=2 or len(set(v))!=2 for v in orders.values()):raise ValueError('Campaign coverage mismatch.')
print(json.dumps({'status':'REFERENCE_CAMPAIGN_EVIDENCE_VERIFIED','runs':count,'http_responses':responses,'disjoint_owned_resources':len(seen),'successful_deletions':deletions,'distinct_orders_per_pair':2,'new_bug_confirmed':False,'server_requests_sent':0},indent=2))
