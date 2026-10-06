"""Native positive same-account dependency acceptance, no Python business workflow."""
import argparse,getpass,hashlib,json,os,re,sys,uuid
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import quote_plus
from run_mealie_generator_live import native,redact,auth_overlay,bundle_review
from audit_mealie_generator_native import audit_events
from render_native_child_lifecycle import render

def interleaving_witness(events):
    """Require a child creation between its ready-parent signal and parent update."""
    parent=None;ready=None;variable=None
    for n,e in enumerate(events):
        data=e.get('data') or {};name=e.get('name')
        if name=='SBT:DependencyReady' and parent is None:parent=data.get('owner');ready=n;variable=data.get('identity_variable')
        if parent and name=='PUT' and '@{'+variable+'}' in data.get('url',''):
            children=[i for i,x in enumerate(events[ready+1:n],ready+1) if x.get('name')=='POST' and '@{'+variable+'}' in x.get('data',{}).get('body','')]
            if children:return {'parent':parent,'ready_event_index':ready,'parent_update_event_index':n,'child_create_events':children}
            return None
    return None

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--username',default='changeme@example.com');p.add_argument('--base-url',default='http://127.0.0.1:9925');p.add_argument('--jar',type=Path)
    a=p.parse_args();root=a.root.resolve();source=root/'generic-generator/generator_v56';contract=root/'generic-generator/compatibility/contracts/mealie.json'
    pins=json.loads(Path(__file__).with_name('mealie_native_acceptance_pins.json').read_text())
    def digest(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
    if digest(contract)!=pins['contract_normalized_sha256']:raise ValueError('Pinned contract differs')
    for name,value in pins['critical_source_normalized_sha256'].items():
        if digest(source/name)!=value:raise ValueError('Installed source differs: '+name)
    run=root/'runs'/('generator-child-lifecycle-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f'));js=run/'model/spec/js';js.mkdir(parents=True);(run/'model/config').mkdir();(run/'model/config/provengo.yml').write_text('version: 2\n')
    report={'status':'PREPARING','resource_scope':'New resources owned by the authenticated account only','full_crud':False,'deletion_tested':True,'automatic_retry':False,'five_findings_reproduced':False,'native_live_executed':False,'application_requests_in_interfaces':True,'business_step_bridge':False,'expected_http_calls':29,'expected_workers':4,'expected_bthreads':20,'contract_normalized_sha256':digest(contract),'critical_source_normalized_sha256':{name:digest(source/name) for name in pins['critical_source_normalized_sha256']},'generator_version_expected':pins['generator_version'],'put_semantics_qualification':'A submitted collection replacement can explain a state difference; a verifier failure alone is not a confirmed bug'}
    secrets=[];environment=os.environ.copy()
    try:
        sys.path.insert(0,str(source.parent));from generator_v56.pipeline import run_pipeline
        seed=uuid.uuid4().int%2147483647;report['seed']=seed
        result=run_pipeline(str(contract),'mealie',a.base_url,seed,include_resource_maps=True)
        namespace='sbt-dep-'+uuid.uuid4().hex[:16];report['namespace']=namespace;report['scheduling_constraint']='Native mutation action transaction: protects refresh/write/readback from other modeled mutations; lifecycle orders remain variable'
        interfaces,stories,manifest=render(result.plan,a.base_url,namespace,'api/households/shopping/lists','api/households/shopping/items')
        doc=json.loads(contract.read_text(encoding='utf-8-sig'));flows=[v.get('flows',{}).get('password') for v in doc['components']['securitySchemes'].values()];flow=next(f for f in flows if f and f.get('tokenUrl'))
        interfaces=interfaces.replace('Bearer @{mealie_acceptance_token}',"Bearer @{getEnv('MEALIE_ACCEPTANCE_TOKEN')}")
        interfaces,stories=auth_overlay(interfaces,stories,flow['tokenUrl'],expected_workers=4)
        (js/'interfaces.mealie.js').write_text(interfaces,encoding='utf-8');(js/'stories.mealie.js').write_text(stories,encoding='utf-8');(run/'dependency-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');(run/'dependency_graph.json').write_text(json.dumps(result.dependency_graph_report,indent=2),encoding='utf-8')
        candidates=run/'samples-candidates.json';response=native(['sample','--algorithm','random','--size','4','--max-length','400','-o',str(candidates),str(run/'model')],a.jar,120,environment)
        (run/'sample-output.txt').write_text(response.stdout+'\n'+response.stderr,encoding='utf-8')
        if response.returncode or not candidates.exists() or candidates.stat().st_size>64*1024*1024:raise ValueError('Native sampling failed or oversized')
        paths=json.loads(candidates.read_text());owners=[w['owner'] for w in manifest['workers']];chosen=None
        for n,events in enumerate(paths,1):
            audit=audit_events([events],owners);witness=interleaving_witness(events)
            finals={e.get('data',{}).get('owner') for e in events if e.get('name')=='SBT:FinalVerified'}
            if audit['status']=='NATIVE_SYMBOLIC_WORKERS_COMPLETE' and witness and finals=={'child:1','child:2'} and any(e.get('name')=='SBT:LifecycleDeleted' for e in events):chosen=n;break
        if chosen is None:raise ValueError('No complete interleaved schedule among four samples; live execution was not started')
        sample=run/'samples.json';sample.write_text(json.dumps([events]),encoding='utf-8');report['selected_candidate']=chosen;report['sample_candidates']=len(paths);report['interleaving_witness']=witness;report['symbolic_audit']=audit
        if audit['status']!='NATIVE_SYMBOLIC_WORKERS_COMPLETE':raise ValueError('Native lifecycle sampling incomplete')
        password=getpass.getpass('Mealie password (hidden): ');secrets=[password,quote_plus(password)];environment['MEALIE_ACCEPTANCE_USERNAME']=quote_plus(a.username);environment['MEALIE_ACCEPTANCE_PASSWORD']=quote_plus(password)
        print('Native child lifecycle: two new lists and two items; delete only the first owned child after verified updates; parents and sibling retained; no retry.',flush=True)
        report['native_live_executed']=True;response=native(['--batch-mode','run','--run-source',str(sample),'--run-id','1',str(run/'model')],a.jar,240,environment)
        log=redact(response.stdout+'\n'+response.stderr,secrets);(run/'live-output.txt').write_text(log,encoding='utf-8');report['native_exit_code']=response.returncode
        receipts=[]
        for line in log.splitlines():
            if 'DEPENDENCY_RECEIPT ' in line:receipts.append(json.loads(line.split('DEPENDENCY_RECEIPT ',1)[1]))
        (run/'response-receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf-8');report['response_receipts']=len(receipts)
        writes=[json.loads(line.split('INTERLEAVED_WRITE_BODY ',1)[1]) for line in log.splitlines() if 'INTERLEAVED_WRITE_BODY ' in line];(run/'write-receipts.json').write_text(json.dumps(writes,indent=2),encoding='utf-8')
        report['status']='NATIVE_CHILD_LIFECYCLE_PASS' if response.returncode==0 and len(receipts)==28 and len(writes)==4 else 'NATIVE_CHILD_LIFECYCLE_NOT_ACCEPTED'
        if response.returncode and any(s in log for s in ['CRUD readback mismatch','Retained parent scalar state changed after child deletion','Deletion parent or sibling membership mismatch','Parent membership readback mismatch','Parent binding changed','Parent collection changed during marker update','Scalar state changed after marker update']):report['status']='STATE_DIFFERENCE_REQUIRES_QUALIFICATION'
        report['qualification']='Native callback readbacks and captured response bodies; no claim of whole-system or bug reproduction coverage'
    except Exception as error:
        report['status']='NATIVE_CHILD_LIFECYCLE_NOT_ACCEPTED';report['error']=redact(str(error),secrets)
    finally:
        environment.pop('MEALIE_ACCEPTANCE_PASSWORD',None);environment.pop('MEALIE_ACCEPTANCE_USERNAME',None)
        (run/'acceptance-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');bundle_review(run);print(report['status']);print('Review ZIP:',run/'review.zip')
    return 0 if report['status']=='NATIVE_CHILD_LIFECYCLE_PASS' else 2
if __name__=='__main__':sys.exit(main())
