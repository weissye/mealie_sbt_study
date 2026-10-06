"""Native positive same-account dependency acceptance, no Python business workflow."""
import argparse,getpass,hashlib,json,os,re,sys,uuid
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import quote_plus
from run_mealie_generator_live import native,redact,auth_overlay,bundle_review
from audit_mealie_generator_native import audit_events
from render_native_distinct_merge import render

def interleaving_witness(events):
    posts=[i for i,e in enumerate(events) if e.get('name')=='POST' and '/shopping/items' in e.get('data',{}).get('url','')]
    if len(posts)<2:return None
    before,after=posts[:2]
    updates=[i for i,e in enumerate(events) if before<i<after and e.get('name')=='PUT']
    optional=[i for i in updates if '@{dep_prereq' in events[i]['data'].get('url','')]
    parents=[i for i in updates if '@{dep_parent' in events[i]['data'].get('url','')]
    if len(optional)!=2 or len(parents)!=2:return None
    return {'first_child_create':before,'second_child_create':after,'prerequisite_updates_between':optional,'parent_updates_between':parents,'binding_policy':'distinct parent instances'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--username',default='changeme@example.com');p.add_argument('--base-url',default='http://127.0.0.1:9925');p.add_argument('--jar',type=Path);p.add_argument('--scenario',choices=['distinct','merge'],required=True)
    a=p.parse_args();root=a.root.resolve();source=root/'generic-generator/generator_v56';contract=root/'generic-generator/compatibility/contracts/mealie.json'
    pins=json.loads(Path(__file__).with_name('mealie_native_acceptance_pins.json').read_text())
    def digest(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
    if digest(contract)!=pins['contract_normalized_sha256']:raise ValueError('Pinned contract differs')
    for name,value in pins['critical_source_normalized_sha256'].items():
        if digest(source/name)!=value:raise ValueError('Installed source differs: '+name)
    run=root/'runs'/('generator-'+a.scenario+'-dependencies-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f'));js=run/'model/spec/js';js.mkdir(parents=True);(run/'model/config').mkdir();(run/'model/config/provengo.yml').write_text('version: 2\n')
    report={'status':'PREPARING','resource_scope':'New resources owned by the authenticated account only','full_crud':False,'deletion_tested':False,'automatic_retry':False,'five_findings_reproduced':False,'native_live_executed':False,'application_requests_in_interfaces':True,'business_step_bridge':False,'expected_http_calls':37,'expected_workers':6,'expected_bthreads':29 if a.scenario=='merge' else 26,'scenario':a.scenario,'contract_normalized_sha256':digest(contract),'critical_source_normalized_sha256':{name:digest(source/name) for name in pins['critical_source_normalized_sha256']},'generator_version_expected':pins['generator_version'],'put_semantics_qualification':'A submitted collection replacement can explain a state difference; a verifier failure alone is not a confirmed bug'}
    secrets=[];environment=os.environ.copy()
    try:
        sys.path.insert(0,str(source.parent));from generator_v56.pipeline import run_pipeline
        seed=uuid.uuid4().int%2147483647;report['seed']=seed
        result=run_pipeline(str(contract),'mealie',a.base_url,seed,include_resource_maps=True)
        namespace='sbt-dep-'+uuid.uuid4().hex[:16];report['namespace']=namespace;report['scheduling_constraint']='Native mutation action transaction: protects refresh/write/readback from other modeled mutations; lifecycle orders remain variable'
        policy=json.loads((root/'profiles/mealie-native-merge-policy.json').read_text(encoding='utf-8-sig'))
        report['explicit_merge_policy']=policy if a.scenario=='merge' else None
        interfaces,stories,manifest=render(result.plan,json.loads(contract.read_text(encoding='utf-8-sig')),a.base_url,namespace,'api/households/shopping/lists','api/households/shopping/items',['api/foods','api/units'],policy,a.scenario)
        doc=json.loads(contract.read_text(encoding='utf-8-sig'));flows=[v.get('flows',{}).get('password') for v in doc['components']['securitySchemes'].values()];flow=next(f for f in flows if f and f.get('tokenUrl'))
        interfaces=interfaces.replace('Bearer @{mealie_acceptance_token}',"Bearer @{getEnv('MEALIE_ACCEPTANCE_TOKEN')}")
        interfaces,stories=auth_overlay(interfaces,stories,flow['tokenUrl'],expected_workers=6)
        (js/'interfaces.mealie.js').write_text(interfaces,encoding='utf-8');(js/'stories.mealie.js').write_text(stories,encoding='utf-8');(run/'dependency-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');(run/'dependency_graph.json').write_text(json.dumps(result.dependency_graph_report,indent=2),encoding='utf-8')
        candidates=run/'samples-candidates.json';response=native(['sample','--algorithm','random','--size','4','--max-length','400','-o',str(candidates),str(run/'model')],a.jar,120,environment)
        (run/'sample-output.txt').write_text(response.stdout+'\n'+response.stderr,encoding='utf-8')
        if response.returncode or not candidates.exists() or candidates.stat().st_size>64*1024*1024:raise ValueError('Native sampling failed or oversized')
        paths=json.loads(candidates.read_text());owners=[w['owner'] for w in manifest['workers']];chosen=None
        for n,events in enumerate(paths,1):
            audit=audit_events([events],owners);witness=interleaving_witness(events)
            finals={e.get('data',{}).get('owner') for e in events if e.get('name')=='SBT:FinalVerified'}
            if audit['status']=='NATIVE_SYMBOLIC_WORKERS_COMPLETE' and witness and finals=={'child:1','child:2'} and (a.scenario=='distinct' or any(e.get('name')=='SBT:MergeFinished' for e in events)):chosen=n;break
        if chosen is None:raise ValueError('No complete interleaved schedule among four samples; live execution was not started')
        sample=run/'samples.json';sample.write_text(json.dumps([events]),encoding='utf-8');report['selected_candidate']=chosen;report['sample_candidates']=len(paths);report['interleaving_witness']=witness;report['symbolic_audit']=audit;report['expected_http_calls']=sum(e.get('name') in ('GET','POST','PUT','PATCH','DELETE') for e in events);report['expected_post_prerequisite_child_reads']=report['expected_http_calls']-(44 if a.scenario=='merge' else 37)
        if audit['status']!='NATIVE_SYMBOLIC_WORKERS_COMPLETE':raise ValueError('Native lifecycle sampling incomplete')
        del paths,events
        __import__('gc').collect()
        password=getpass.getpass('Mealie password (hidden): ');secrets=[password,quote_plus(password)];environment['MEALIE_ACCEPTANCE_USERNAME']=quote_plus(a.username);environment['MEALIE_ACCEPTANCE_PASSWORD']=quote_plus(password)
        print('Native '+a.scenario+' acceptance: distinct lists share food/unit; '+('one additional merge contribution; ' if a.scenario=='merge' else '')+'all resources retained; no live retry.',flush=True)
        report['native_live_executed']=True;response=native(['--batch-mode','run','--run-source',str(sample),'--run-id','1',str(run/'model')],a.jar,240,environment)
        log=redact(response.stdout+'\n'+response.stderr,secrets);(run/'live-output.txt').write_text(log,encoding='utf-8');report['native_exit_code']=response.returncode
        receipts=[]
        for line in log.splitlines():
            if 'DEPENDENCY_RECEIPT ' in line:receipts.append(json.loads(line.split('DEPENDENCY_RECEIPT ',1)[1]))
        (run/'response-receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf-8');report['response_receipts']=len(receipts);report['post_prerequisite_child_reads']=sum(x['operation'].startswith('depObservechild') for x in receipts)
        writes=[json.loads(line.split('INTERLEAVED_WRITE_BODY ',1)[1]) for line in log.splitlines() if 'INTERLEAVED_WRITE_BODY ' in line];(run/'write-receipts.json').write_text(json.dumps(writes,indent=2),encoding='utf-8')
        report['status']='NATIVE_DISTINCT_MERGE_PASS' if response.returncode==0 and len(receipts)==report['expected_http_calls']-1 and len(writes)==6 else 'NATIVE_DISTINCT_MERGE_NOT_ACCEPTED'
        if response.returncode and any(s in log for s in ['Prerequisite scalar state changed','Prerequisite readback mismatch','Optional dependency readback mismatch','Create optional binding mismatch','CRUD readback mismatch','Parent membership readback mismatch','Parent binding changed','Parent collection changed during marker update','Scalar state changed after marker update','MERGE_ENVELOPE_MISMATCH','MERGE_RESPONSE_STATE_MISMATCH','MERGE_PERSISTED_STATE_MISMATCH','MERGE_EMBEDDED_IDENTITY_MISMATCH','MERGE_PARENT_VIEW_MISMATCH']):report['status']='STATE_DIFFERENCE_REQUIRES_QUALIFICATION'
        # Require independent distinct identities and bindings, regardless of envelope capture.
        creates=[x['body'] for x in receipts if x['operation'] in ('depCreatechild1','depCreatechild2')]
        actual=[b.get('createdItems',[None])[0] if len(b.get('createdItems',[]))==1 else None for b in creates]
        report['distinct_children_verified']=len(actual)==2 and all(actual) and actual[0]['id']!=actual[1]['id'] and actual[0]['shoppingListId']!=actual[1]['shoppingListId']
        merge_operations={x['operation'] for x in receipts}
        report['merge_independent_readbacks_present']=all(name in merge_operations for name in ('depMergeAdd','depMergeReadback','depMergeParentReadback')) if a.scenario=='merge' else None
        if report['post_prerequisite_child_reads']!=report['expected_post_prerequisite_child_reads']:report['status']='NATIVE_DISTINCT_MERGE_NOT_ACCEPTED'
        if not report['distinct_children_verified'] or (a.scenario=='merge' and not report['merge_independent_readbacks_present']):report['status']='NATIVE_DISTINCT_MERGE_NOT_ACCEPTED'
        report['new_bug_confirmed']=False
        report['qualification']='Native callback readbacks and captured response bodies; no claim of whole-system or bug reproduction coverage'
    except Exception as error:
        report['status']='NATIVE_DISTINCT_MERGE_NOT_ACCEPTED';report['error']=redact(str(error),secrets)
    finally:
        environment.pop('MEALIE_ACCEPTANCE_PASSWORD',None);environment.pop('MEALIE_ACCEPTANCE_USERNAME',None)
        (run/'acceptance-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');bundle_review(run);print(report['status']);print('Review ZIP:',run/'review.zip')
    return 0 if report['status']=='NATIVE_DISTINCT_MERGE_PASS' else 2
if __name__=='__main__':sys.exit(main())
