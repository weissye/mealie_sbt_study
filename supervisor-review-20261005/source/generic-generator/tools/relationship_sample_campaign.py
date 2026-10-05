"""Validate and bundle multiple replay reviews from one audited native sample file."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

if __package__:
    from .relationship_execution import find_receipt, redact, validate_negative_receipts, validate_legal_receipts, validate_shared_update_receipts, validate_deletion_receipts, validate_semantic_receipts
else:
    from relationship_execution import find_receipt, redact, validate_negative_receipts, validate_legal_receipts, validate_shared_update_receipts, validate_deletion_receipts, validate_semantic_receipts


def evaluate_review(path):
    with zipfile.ZipFile(path) as archive:
        files = {name.replace('\\','/'): archive.read(name) for name in archive.namelist()}
    plan=json.loads(files['relationship_scenario_plan.json'])
    compilation=json.loads(files['relationship_compilation.json'])
    sample=json.loads(files['execution-review/sample-acceptance.json'])
    live=json.loads(files['execution-review/run-acceptance.json'])
    if sample.get('status')!='NATIVE_SYMBOLIC_SAMPLES_COMPLETE':
        raise ValueError('Native sampling was not accepted.')
    for name,digest in sample['model_sha256'].items():
        if hashlib.sha256(files[name.replace('\\','/')]).hexdigest()!=digest:
            raise ValueError('Native model checksum mismatch.')
    if live.get('live_accepted') is not True or live.get('native_exit_code')!=0 or live.get('status')!='NATIVE_RELATIONSHIP_CALLBACKS_PASS':
        raise ValueError('Replay was not accepted: '+str(live.get('error',live.get('status'))))
    sample_id=live.get('sample_id')
    if type(sample_id) is not int or not 1<=sample_id<=len(sample['task_orders']):
        raise ValueError('Invalid native sample identity.')
    tasks={t['id']:t for t in plan['tasks']};order=sample['task_orders'][sample_id-1];done=set()
    for task_id in order:
        if task_id not in tasks or task_id in done or not set(tasks[task_id]['after']).issubset(done):
            raise ValueError('Native task order violates generated dependencies.')
        done.add(task_id)
    if done!=set(tasks):raise ValueError('Incomplete native task order.')
    log=files['execution-review/run-output.txt'].decode('utf-8')
    executed=[]
    active = None; task_methods = {}
    for line in log.splitlines():
        if 'Selected: [SBT:RelTask ' in line:
            active = re.search(r'id:"([^"]+)"',line).group(1)
            task_methods[active] = []
        if 'Selected:' in line and 'lib:"REST"' in line and active:
            task_methods[active].append(re.search(r'method:"([^"]+)"',line).group(1))
        if 'Selected: [SBT:RelTaskDone ' in line:
            executed.append(re.search(r'id:"([^"]+)"',line).group(1))
            active = None
    receipt=find_receipt(log)
    if executed!=order or not receipt or receipt!=live.get('runtime_receipt'):
        raise ValueError('Live receipt/task order differs from native log.')
    if receipt.get('task_count')!=len(tasks) or receipt.get('response_count')!=compilation['http_requests_per_complete_schedule'] or receipt.get('owned_instances')!=sum(map(len,plan['instances'].values())):
        raise ValueError('Incomplete native execution counts.')
    if sum('Selected:' in line and 'lib:"REST"' in line for line in log.splitlines())!=receipt['response_count']:
        raise ValueError('Selected HTTP event count differs from callback receipt.')
    for validator in [validate_negative_receipts,validate_legal_receipts,validate_shared_update_receipts,validate_deletion_receipts,validate_semantic_receipts]:validator(receipt,plan)
    for task in tasks.values():
        if task['kind'] == 'attached_delete':
            count = len(task['checks'])
            expected_methods = ['GET']*(count+1) + ['DELETE'] + ['GET']*(count+1)
            if task_methods.get(task['id']) != expected_methods:
                raise ValueError('Attached deletion log includes a detach write or lacks required readbacks.')
    for task in tasks.values():
        if task['kind'] == 'semantic_merge':
            expected = ['GET','GET',task['operation'].split(' ')[0],'GET','GET'] + ['GET']*len(task['checks'])
        elif task['kind'] == 'semantic_contribution':
            expected = ['GET','POST'] + ['GET']*len(task['checks'])
        else:
            continue
        if task_methods.get(task['id']) != expected:
            raise ValueError('Semantic mutation log lacks its required independent readbacks.')
    mutation_order=[t for t in order if tasks[t]['kind'] in ('shared_update','detached_delete','attached_delete','semantic_merge','semantic_contribution')]
    construction = {}
    if compilation.get('mutate_during_construction'):
        first = min(order.index(t) for t in mutation_order)
        remaining = [t for t in order[first+1:] if tasks[t]['kind'] == 'qualified_action' or (tasks[t]['kind'] == 'link' and not tasks[t].get('lifecycle_phase'))]
        if not remaining:
            raise ValueError('No mutation was observed during relationship construction.')
        construction = {'construction_tasks_after_first_mutation':len(remaining),
                        'initial_links_after_first_mutation':sum(tasks[t]['kind']=='link' for t in remaining),
                        'attached_deletion_count':sum(tasks[t]['kind']=='attached_delete' for t in mutation_order)}
    if plan.get('semantic_program'):
        construction.update(semantic_family=plan['semantic_program']['family'],
                            merge_count=sum(t['kind']=='semantic_merge' for t in tasks.values()),
                            contribution_count=sum(t['kind']=='semantic_contribution' for t in tasks.values()))
    return dict({'status':'NATIVE_RELATIONSHIP_CALLBACKS_PASS','sample_id':sample_id,
            'model_sha256':sample['model_sha256'],'samples_sha256':sample['samples_sha256'],
            'task_order_sha256':hashlib.sha256(json.dumps(order).encode()).hexdigest(),
            'mutation_order':mutation_order,'mutation_order_sha256':hashlib.sha256(json.dumps(mutation_order).encode()).hexdigest(),
            'task_count':receipt['task_count'],'response_count':receipt['response_count'],
            'shared_update_count':len(receipt.get('shared_updates',[])),
            'deletion_count':len(receipt.get('detached_deletions',[]))}, **construction)


def summarize_reviews(paths, expected_runs):
    runs=[];identities=set();baseline=None
    for path in paths:
        try:
            run=evaluate_review(path);identity=(run['samples_sha256'],run['sample_id'])
            if identity in identities:raise ValueError('Duplicate sample cannot count as another campaign run.')
            signatures=(run['model_sha256'],run['samples_sha256'])
            if baseline is not None and signatures!=baseline:raise ValueError('Reviews must use the same model and native sample file.')
            identities.add(identity);baseline=signatures;runs.append(dict(run,review=Path(path).name))
        except (ValueError,KeyError,TypeError,OSError,zipfile.BadZipFile) as error:
            runs.append({'status':'NOT_ACCEPTED','review':Path(path).name,'error':redact(str(error))})
    passed=[r for r in runs if r['status']=='NATIVE_RELATIONSHIP_CALLBACKS_PASS']
    complete=len(runs)==expected_runs and len(passed)==expected_runs
    return {'status':'CONSISTENCY_CAMPAIGN_PASS' if complete else 'CONSISTENCY_CAMPAIGN_NOT_ACCEPTED',
            'expected_runs':expected_runs,'accepted_runs':len(passed),
            'distinct_task_orders':len({r['task_order_sha256'] for r in passed}),
            'distinct_mutation_orders':len({r['mutation_order_sha256'] for r in passed}),
            'runs':runs,'collector_server_requests':0,'automatic_retry':False,'reset_replay_accepted':False}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reviews',nargs='+',type=Path,required=True)
    parser.add_argument('--expected-runs',type=int,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=summarize_reviews(args.reviews,args.expected_runs)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('campaign-acceptance.json',json.dumps(report,indent=2))
        for index,path in enumerate(args.reviews,1):
            if path.is_file():archive.write(path,'live-'+str(index)+'.zip')
    print(report['status']);print('Distinct mutation orders: '+str(report['distinct_mutation_orders']));print('Campaign ZIP: '+str(args.output))
    return 0 if report['status']=='CONSISTENCY_CAMPAIGN_PASS' else 1

if __name__=='__main__':sys.exit(main())
