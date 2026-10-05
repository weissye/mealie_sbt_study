"""Extract exact copy write/read observations from preserved native logs; no HTTP."""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path


def extract(output):
    records={}
    decoder=json.JSONDecoder()
    for match in re.finditer(r"setting '(rel_copy_test_[^']*)' to '(\{)",output):
        try:record,_=decoder.raw_decode(output[match.start(2):])
        except ValueError:continue
        if isinstance(record,dict) and 'task_id' in record:records[match.group(1)]=record
    return list(records.values())


def export(review):
    with zipfile.ZipFile(review) as archive:
        output=archive.read('execution-review/run-output.txt').decode('utf-8-sig')
        acceptance=json.loads(archive.read('execution-review/run-acceptance.json').decode('utf-8-sig'))
        plan=json.loads(archive.read('relationship_scenario_plan.json').decode('utf-8-sig'))
    records=extract(output)
    if not records:records=acceptance.get('runtime_receipt',{}).get('copy_isolations',[])
    tasks=[t for t in plan['tasks'] if t['kind']=='copy_isolation']
    for record in records:
        task=next((t for t in tasks if t['id']==record['task_id']),None)
        if task is None:raise ValueError('Unknown recorded copy task.')
        for row in record.get('observations',[]):
            if not isinstance(row.get('body'),str) or not isinstance(row.get('code'),(int,float)):
                raise ValueError('Incomplete raw response observation.')
            if row.get('kind')=='write' and not isinstance(row.get('request_body'),str):
                raise ValueError('Missing exact write body.')
    count=sum(len(r.get('observations',[])) for r in records)
    return dict(status='RAW_COPY_OBSERVATIONS_EXTRACTED' if count else 'NO_COPY_OBSERVATIONS_REACHED',
                review_sha256=hashlib.sha256(Path(review).read_bytes()).hexdigest(),
                resource_mutations_by_extractor=0,new_bug_confirmed=False,
                observations=count,copy_records=records,
                limitation='Partial runs retain only observations reached before failure. A failure is a candidate until independently qualified.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--review',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    report=export(Path(a.review));Path(a.output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(report['status']+': '+str(report['observations']))
