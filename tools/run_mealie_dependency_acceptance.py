"""Native positive same-account dependency acceptance, no Python business workflow."""
import argparse,getpass,hashlib,json,os,re,sys,uuid
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import quote_plus
from run_mealie_generator_live import native,redact,auth_overlay,bundle_review
from audit_mealie_generator_native import audit_events
from render_native_dependency_acceptance import render

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--username',default='changeme@example.com');p.add_argument('--base-url',default='http://127.0.0.1:9925');p.add_argument('--jar',type=Path)
    a=p.parse_args();root=a.root.resolve();source=root/'generic-generator/generator_v56';contract=root/'generic-generator/compatibility/contracts/mealie.json'
    pins=json.loads(Path(__file__).with_name('mealie_native_acceptance_pins.json').read_text())
    def digest(path):return hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
    if digest(contract)!=pins['contract_normalized_sha256']:raise ValueError('Pinned contract differs')
    for name,value in pins['critical_source_normalized_sha256'].items():
        if digest(source/name)!=value:raise ValueError('Installed source differs: '+name)
    run=root/'runs'/('generator-dependency-acceptance-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f'));js=run/'model/spec/js';js.mkdir(parents=True);(run/'model/config').mkdir();(run/'model/config/provengo.yml').write_text('version: 2\n')
    report={'status':'PREPARING','resource_scope':'New resources owned by the authenticated account only','full_crud':False,'deletion_tested':False,'automatic_retry':False,'five_findings_reproduced':False,'native_live_executed':False,'application_requests_in_interfaces':True,'business_step_bridge':False,'expected_http_calls':19,'expected_workers':4,'expected_bthreads':14,'contract_normalized_sha256':digest(contract),'critical_source_normalized_sha256':{name:digest(source/name) for name in pins['critical_source_normalized_sha256']},'generator_version_expected':pins['generator_version']}
    secrets=[];environment=os.environ.copy()
    try:
        sys.path.insert(0,str(source.parent));from generator_v56.pipeline import run_pipeline
        seed=uuid.uuid4().int%2147483647;report['seed']=seed
        result=run_pipeline(str(contract),'mealie',a.base_url,seed,include_resource_maps=True)
        namespace='sbt-dep-'+uuid.uuid4().hex[:16];report['namespace']=namespace
        interfaces,stories,manifest=render(result.plan,a.base_url,namespace,'api/households/shopping/lists','api/households/shopping/items')
        doc=json.loads(contract.read_text(encoding='utf-8-sig'));flows=[v.get('flows',{}).get('password') for v in doc['components']['securitySchemes'].values()];flow=next(f for f in flows if f and f.get('tokenUrl'))
        interfaces=interfaces.replace('Bearer @{mealie_acceptance_token}',"Bearer @{getEnv('MEALIE_ACCEPTANCE_TOKEN')}")
        interfaces,stories=auth_overlay(interfaces,stories,flow['tokenUrl'],expected_workers=4)
        (js/'interfaces.mealie.js').write_text(interfaces,encoding='utf-8');(js/'stories.mealie.js').write_text(stories,encoding='utf-8');(run/'dependency-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');(run/'dependency_graph.json').write_text(json.dumps(result.dependency_graph_report,indent=2),encoding='utf-8')
        sample=run/'samples.json';response=native(['sample','--algorithm','random','--size','1','--max-length','300','-o',str(sample),str(run/'model')],a.jar,120,environment)
        (run/'sample-output.txt').write_text(response.stdout+'\n'+response.stderr,encoding='utf-8')
        if response.returncode or not sample.exists() or sample.stat().st_size>32*1024*1024:raise ValueError('Native sampling failed or oversized')
        owners=[w['owner'] for w in manifest['workers']];audit=audit_events(json.loads(sample.read_text()),owners);report['symbolic_audit']=audit
        if audit['status']!='NATIVE_SYMBOLIC_WORKERS_COMPLETE':raise ValueError('Native lifecycle sampling incomplete')
        password=getpass.getpass('Mealie password (hidden): ');secrets=[password,quote_plus(password)];environment['MEALIE_ACCEPTANCE_USERNAME']=quote_plus(a.username);environment['MEALIE_ACCEPTANCE_PASSWORD']=quote_plus(password)
        print('Native dependency acceptance: two new lists and two new items in the same account; create/read/update/readback; retained; no deletion or retry.',flush=True)
        report['native_live_executed']=True;response=native(['--batch-mode','run','--run-source',str(sample),'--run-id','1',str(run/'model')],a.jar,240,environment)
        log=redact(response.stdout+'\n'+response.stderr,secrets);(run/'live-output.txt').write_text(log,encoding='utf-8');report['native_exit_code']=response.returncode
        receipts=[]
        for line in log.splitlines():
            if 'DEPENDENCY_RECEIPT ' in line:receipts.append(json.loads(line.split('DEPENDENCY_RECEIPT ',1)[1]))
        (run/'response-receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf-8');report['response_receipts']=len(receipts)
        report['status']='NATIVE_DEPENDENCY_FUNCTIONAL_ACCEPTANCE_PASS' if response.returncode==0 and len(receipts)==18 else 'NATIVE_DEPENDENCY_FUNCTIONAL_ACCEPTANCE_NOT_ACCEPTED'
        report['qualification']='Native callback readbacks and captured response bodies; no claim of whole-system or bug reproduction coverage'
    except Exception as error:
        report['status']='NATIVE_DEPENDENCY_FUNCTIONAL_ACCEPTANCE_NOT_ACCEPTED';report['error']=redact(str(error),secrets)
    finally:
        environment.pop('MEALIE_ACCEPTANCE_PASSWORD',None);environment.pop('MEALIE_ACCEPTANCE_USERNAME',None)
        (run/'acceptance-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');bundle_review(run);print(report['status']);print('Review ZIP:',run/'review.zip')
    return 0 if report['status']=='NATIVE_DEPENDENCY_FUNCTIONAL_ACCEPTANCE_PASS' else 2
if __name__=='__main__':sys.exit(main())
