"""Bounded positive functional acceptance using native generated Provengo CRUD."""
import argparse
import getpass
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

def redact(text, secrets):
    secrets = list(secrets) + re.findall(r"RTV: setting 'mealie_acceptance_token' to '([^']+)'", text)
    for secret in sorted(set(secrets), key=len, reverse=True):
        if secret:
            text = text.replace(secret, '<REDACTED>')
    text = re.sub(r'(?i)(Bearer\s+)[^\s"\}\],]+', r'\1<REDACTED>', text)
    text = re.sub(r'(?i)(["\x27]access_token["\x27]\s*:\s*["\x27])[^"\x27]+', r'\1<REDACTED>', text)
    return text

def auth_overlay(interfaces, stories, token_path, expected_workers=2):
    old = "Bearer @{getEnv('MEALIE_ACCEPTANCE_TOKEN')}"
    if old not in interfaces:
        raise ValueError('Generated authorization hook missing')
    interfaces = interfaces.replace(old, 'Bearer @{mealie_acceptance_token}')
    interfaces += '\nfunction acceptanceLogin(){svc.post(' + json.dumps(token_path) + ''',{
      headers:{"Content-Type":"application/x-www-form-urlencoded"},
      body:"username=@{getEnv('MEALIE_ACCEPTANCE_USERNAME')}&password=@{getEnv('MEALIE_ACCEPTANCE_PASSWORD')}",
      expectedResponseCodes:[200],callback:function(response){
        var token=JSON.parse(response.body).access_token;
        if(typeof token!=="string"||!token)throw new Error("OAuth token missing");
        pvg.rtv.set("mealie_acceptance_token",token);
      }});}
'''
    pattern = r'(bthread\("crud:[^"\n]+", function\(\)\s*\{)'
    if len(re.findall(r'bthread\("crud:',stories)) != expected_workers:
        raise ValueError('Unexpected generated CRUD worker count')
    stories += '\nbthread("acceptance:authentication",function(){acceptanceLogin();sync({request:Event("SBT:LiveAuthReady")});});\n'
    return interfaces, stories

def native(arguments, jar, timeout, environment):
    if jar:
        command = ['java','-Xmx1g','-jar',str(jar.resolve())] + arguments
    else:
        exe = shutil.which('provengo')
        if not exe:
            raise ValueError('Provengo missing; supply --jar')
        command = [exe] + arguments
        if os.name == 'nt' and exe.lower().endswith(('.bat','.cmd')):
            if any(any(c in a for c in ('"','\r','\n','%','\0')) for a in command):
                raise ValueError('Unsupported batch argument')
            command = subprocess.list2cmdline([os.environ.get('COMSPEC','cmd.exe')]) + ' /d /s /v:off /c "' + ' '.join('"'+a+'"' for a in command) + '"'
    return subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',
                          timeout=timeout,env=environment)

def bundle_review(run):
    """Exclude native internal products, which can retain authentication responses."""
    with zipfile.ZipFile(run/'review.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(run.rglob('*')):
            if p.is_file() and p.name!='review.zip' and 'products' not in p.relative_to(run).parts:
                archive.write(p,p.relative_to(run).as_posix())

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--username',default='changeme@example.com')
    parser.add_argument('--base-url',default='http://127.0.0.1:9925')
    parser.add_argument('--jar',type=Path)
    args=parser.parse_args()
    root=args.root.resolve()
    contract=root/'generic-generator/compatibility/contracts/mealie.json'
    source=root/'generic-generator/generator_v56'
    doc=json.loads(contract.read_text(encoding='utf-8-sig'))
    pins=json.loads(Path(__file__).with_name('mealie_native_acceptance_pins.json').read_text())
    raw=contract.read_bytes()
    if hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()!=pins['contract_normalized_sha256']:
        raise ValueError('Pinned contract differs')
    for name,expected in pins['critical_source_normalized_sha256'].items():
        if hashlib.sha256((source/name).read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=expected:
            raise ValueError('Critical installed source differs: '+name)
    # Explicit positive acceptance scope. No merge/copy/ownership probes.
    collection='/api/organizers/tags'
    item=collection+'/{item_id}'
    scope={collection:{'post':doc['paths'][collection]['post']},
           item:{m:doc['paths'][item][m] for m in ['get','put']}}
    flows=[scheme.get('flows',{}).get('password') for scheme in doc['components']['securitySchemes'].values()]
    flow=next((f for f in flows if f and f.get('tokenUrl')),None)
    if not flow:
        raise ValueError('OpenAPI password flow absent')
    token_path=flow['tokenUrl']
    if token_path not in doc['paths'] or 'post' not in doc['paths'][token_path]:
        raise ValueError('Documented token operation absent')
    run=root/'runs'/('generator-live-acceptance-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f'))
    js=run/'model/spec/js';js.mkdir(parents=True)
    (run/'model/config').mkdir()
    (run/'model/config/provengo.yml').write_text('version: 2\n')
    projection=dict(doc,paths=scope)
    projected=run/'openapi-scope.json'
    projected.write_text(json.dumps(projection),encoding='utf-8')
    sys.path.insert(0,str(source.parent))
    from generator_v56.pipeline import run_pipeline
    seed=uuid.uuid4().int % 2147483647
    result=run_pipeline(str(projected),'mealie',args.base_url,seed,story_profile='parallel-crud',
                        instances_per_entity=2,logical_processes=1,auth_token_env='MEALIE_ACCEPTANCE_TOKEN')
    from render_native_functional_acceptance import render
    interfaces,stories=render(result.plan,args.base_url,'sbt-acceptance-'+uuid.uuid4().hex[:16])
    # The compatibility renderer already uses the runtime token placeholder.
    interfaces=interfaces.replace('Bearer @{mealie_acceptance_token}', "Bearer @{getEnv('MEALIE_ACCEPTANCE_TOKEN')}")
    interfaces,stories=auth_overlay(interfaces,stories,token_path)
    (js/'interfaces.mealie.js').write_text(interfaces,encoding='utf-8')
    (js/'stories.mealie.js').write_text(stories,encoding='utf-8')
    (run/'generation_report.json').write_text(json.dumps(result.generation_report,indent=2),encoding='utf-8')
    report={'status':'PREPARING','seed':seed,'scope':'Two new tag create/read/update/readback lifecycles',
            'application_requests_in_interfaces':True,'business_step_bridge':False,
            'delete_operations':0,'automatic_retry':False,'five_findings_reproduced':False,
            'credentials_source':'interactive environment only','authentication_overlay':'OpenAPI OAuth password flow',
            'scope_selection':'Explicit bounded acceptance subset; not automatic whole-system coverage',
            'semantic_runtime_profiles_supplied':False,'native_live_executed':False,
            'renderer':'New bounded Gitea-style compatibility renderer over generator_v56 Plan',
            'original_parallel_crud_native_compatibility':'Incomplete in local sampling; not claimed fixed'}
    secrets=[]
    environment=os.environ.copy()
    try:
        sample=run/'samples.json'
        response=native(['sample','--algorithm','random','--size','1','--max-length','160','-o',str(sample),str(run/'model')],args.jar,90,environment)
        (run/'sample-output.txt').write_text(response.stdout+'\n'+response.stderr,encoding='utf-8')
        if response.returncode or not sample.exists() or sample.stat().st_size>16*1024*1024:
            raise ValueError('Native sampling failed or output oversized')
        from audit_mealie_generator_native import audit_events
        workers=re.findall(r'bthread\("crud:([^"\n]+)"',stories)
        audit=audit_events(json.loads(sample.read_text()),workers)
        report['symbolic_audit']=audit
        if audit['status']!='NATIVE_SYMBOLIC_WORKERS_COMPLETE':
            raise ValueError('Symbolic lifecycles incomplete; live execution blocked')
        password=getpass.getpass('Mealie password (hidden): ')
        secrets=[password,quote_plus(password)]
        environment['MEALIE_ACCEPTANCE_USERNAME']=quote_plus(args.username)
        environment['MEALIE_ACCEPTANCE_PASSWORD']=quote_plus(password)
        print('Native live acceptance: two new tags; tags retained; no deletion or retry.',flush=True)
        report['native_live_executed']=True
        response=native(['--batch-mode','run','--run-source',str(sample),'--run-id','1',str(run/'model')],args.jar,180,environment)
        text=redact(response.stdout+'\n'+response.stderr,secrets)
        (run/'live-output.txt').write_text(text,encoding='utf-8')
        report['native_exit_code']=response.returncode
        report['status']='NATIVE_LIVE_FUNCTIONAL_ACCEPTANCE_PASS' if response.returncode==0 else 'NATIVE_LIVE_FUNCTIONAL_ACCEPTANCE_NOT_ACCEPTED'
        report['qualification']='Native exit and generated callback checks; independent external receipt qualification still pending'
    except Exception as error:
        report['status']='NATIVE_LIVE_FUNCTIONAL_ACCEPTANCE_NOT_ACCEPTED'
        report['error']=redact(str(error),secrets)
    finally:
        environment.pop('MEALIE_ACCEPTANCE_PASSWORD',None)
        environment.pop('MEALIE_ACCEPTANCE_USERNAME',None)
        (run/'acceptance-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        bundle_review(run)
        print(report['status']);print('Review ZIP:',run/'review.zip')
    return 0 if report['status']=='NATIVE_LIVE_FUNCTIONAL_ACCEPTANCE_PASS' else 2

if __name__=='__main__':
    sys.exit(main())
