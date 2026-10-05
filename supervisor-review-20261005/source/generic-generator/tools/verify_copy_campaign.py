"""Offline campaign integrity, qualification and reproducibility inventory."""
import argparse,hashlib,json,zipfile,io
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.copy_receipts import validate_copy_receipts,CopyMismatch


def verify(path):
    results=[];owned_ids=set()
    with zipfile.ZipFile(path) as archive:
        names={}
        for name in archive.namelist():
            key=name.replace('\\','/')
            if key in names:raise ValueError('Ambiguous normalized archive path: '+key)
            names[key]=name
        if 'campaign-summary.json' not in names:raise ValueError('Campaign summary missing.')
        summary=json.loads(archive.read(names['campaign-summary.json']).decode('utf-8-sig'))
        runs=summary['runs'];required={(case,sample) for case in ('control','source-first','copy-first','internal-reference') for sample in (1,2)}
        observed={(r['case'],r['sample']) for r in runs}
        if len(runs)!=8 or observed!=required:raise ValueError('Eight complete campaign entries required.')
        for run in runs:
            key=run['case']+'/live-'+str(run['sample'])+'.zip'
            payload=archive.read(names[key]);digest=hashlib.sha256(payload).hexdigest()
            if digest.lower()!=run['sha256'].lower():raise ValueError('Nested review checksum mismatch: '+key)
            with zipfile.ZipFile(io.BytesIO(payload)) as live:
                acceptance=json.loads(live.read('execution-review/run-acceptance.json').decode('utf-8-sig'));plan=json.loads(live.read('relationship_scenario_plan.json').decode('utf-8-sig'))
                receipt=acceptance.get('runtime_receipt')
                if not receipt:raise ValueError('No full copy receipt: '+key)
                ids=[r['route'].get('id') for r in receipt.get('owned_records',[])]
                if len(ids)!=13 or None in ids or len(set(ids))!=13 or owned_ids.intersection(ids):raise ValueError('Campaign did not use distinct fresh owned resource identities.')
                owned_ids.update(ids)
                try:validate_copy_receipts(receipt,plan);status='PASS'
                except CopyMismatch as error:status='COPY_CANDIDATE';failure=str(error)
                if status=='PASS' and acceptance.get('live_accepted') is not True and acceptance.get('native_exit_code')!=0:raise ValueError('Independent copy checks passed but complete native execution missing: '+key)
                if receipt.get('task_count')!=len(plan['tasks']) or receipt.get('owned_instances')!=sum(len(v) for v in plan['instances'].values()):raise ValueError('Incomplete native task/ownership receipt.')
                if run['case']=='control' and status!='PASS':raise ValueError('Matched control failed.')
                item={'case':run['case'],'sample':run['sample'],'status':status,'original_status':run['status'],'original_live_accepted':acceptance.get('live_accepted',False),'sha256':digest}
                if status!='PASS':item['failure']=failure
                results.append(item)
    return {'status':'COPY_CAMPAIGN_EVIDENCE_VERIFIED','campaign_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'runs':results,'distinct_owned_identities':len(owned_ids),'new_bug_confirmed':False,'reset_replay_accepted':False,'resource_mutations_by_verifier':0}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--campaign',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    result=verify(Path(args.campaign));Path(args.output).write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
