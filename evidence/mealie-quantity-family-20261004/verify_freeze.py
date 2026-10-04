"""Verify archived evidence offline without API requests or source modifications."""
import copy,hashlib,io,json,re,sys,zipfile
from pathlib import Path
from semantic_receipts import validate_semantic_receipts
BASE=Path(__file__).resolve().parent

def inspect(raw,label):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        plan=json.loads(z.read('relationship_scenario_plan.json'))
        lines=z.read('execution-review/run-output.txt').decode('utf-8-sig').splitlines()
        acceptance=json.loads(z.read('execution-review/run-acceptance.json'))
    values={}
    for line in lines:
        m=re.search(r"RTV: setting '([^']+)' to '(.*)'$",line)
        if m:
            try:values[m[1]]=json.loads(m[2])
            except ValueError:pass
    records=values['sbt_rel_semantic_receipts'];ids={r['task_id'] for r in records}
    prefix=copy.deepcopy(plan)
    prefix['tasks']=[t for t in plan['tasks'] if not t['kind'].startswith('semantic_') or t['id'] in ids]
    validate_semantic_receipts({'semantic_tests':records,'owned_records':values['sbt_rel_owned']},prefix)
    out={'review':label,'completed_semantic':len(records),'prefix_validation':'PASS','order':[r['task_id'] for r in records],'owned_ids':[r['route']['id'] for r in values['sbt_rel_owned']]}
    if acceptance.get('live_accepted'):
        validate_semantic_receipts({'semantic_tests':records,'owned_records':values['sbt_rel_owned']},plan)
        assert any('Test Result: SUCCESS' in l for l in lines)
        final=records[-1]['expected']
        out.update(status='PASS',final_manual_totals=[sum(final[i]['totals'].values()) for i in plan['instances']['api/households/shopping/lists']])
    else:
        warning=next(l for l in lines if ' WARN [' in l and 'FAIL: Semantic consistency mismatch:' in l)
        failure=json.loads(warning.split('FAIL: Semantic consistency mismatch: ',1)[1].removesuffix('.'))
        pending=next(v for k,v in values.items() if k.endswith('_semantic') and isinstance(v,dict) and v.get('task_id') not in ids and v.get('container')==failure['instance'])
        before=pending['before'][pending['container']]['totals'];source=pending['reference_instance'];recipe=pending['before'][source]['totals']
        fresh=next(c['observed'] for c in pending['checks'] if c['instance']==source)
        assert fresh['totals']==recipe
        expected=copy.deepcopy(before)
        for k,v in recipe.items():expected[k]=expected.get(k,0)+pending['amount']*v
        for k in set(expected)|set(failure['expected']['totals']):assert abs(expected.get(k,0)-failure['expected']['totals'].get(k,0))<1e-8
        assert failure['expected']['references']==failure['observed']['references']
        assert failure['expected']['totals']!=failure['observed']['totals']
        out.update(status='SEMANTIC_DISCREPANCY',task_id=pending['task_id'],amount=pending['amount'],before=before,fresh_recipe=recipe,expected=failure['expected'],observed=failure['observed'])
    return out

def main():
    manifest=json.loads((BASE/'checksums.json').read_text())
    for relative,expected in manifest.items():
        path=BASE/relative
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Checksum mismatch: '+relative)
    runs=[]
    for name in ['original-collision.zip','scaling-controls.zip','integer-merge-lifecycle.zip','removal-isolation-controls.zip']:
        with zipfile.ZipFile(BASE/'originals'/name) as z:
            for n in z.namelist():
                if re.search(r'live-[123]\.zip$',n):runs.append(inspect(z.read(n),name+'/'+n.replace('\\','/')))
    runs.append(inspect((BASE/'originals/original-confirmation.zip').read_bytes(),'original-confirmation.zip'))
    assert len(runs)==24
    assert sum(r['status']=='PASS' for r in runs)==6
    assert sum(r['status']=='SEMANTIC_DISCREPANCY' for r in runs)==18
    result={'status':'ARCHIVE_AND_SEMANTIC_EVIDENCE_VERIFIED','server_requests':0,'run_count':24,'semantic_discrepancies':18,'successful_runs':6,'confirmed_internal_root_cause':False,'confirmed_independent_bug_count':None,'runs':runs}
    if '--output' in sys.argv:
        Path(sys.argv[sys.argv.index('--output')+1]).write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='runs'},indent=2))
if __name__=='__main__':main()
