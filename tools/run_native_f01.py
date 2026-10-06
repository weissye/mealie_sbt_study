"""Offline generation + native CLI sampling/replay. Sends no Python HTTP calls."""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, sys, uuid, zipfile
from pathlib import Path


def execute(cmd,cwd,output,env=None):
    with output.open('w',encoding='utf-8') as f:
        r=subprocess.run(cmd,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
    return r.returncode


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--openapi');p.add_argument('--base-url',default='http://127.0.0.1:9925');p.add_argument('--jar');p.add_argument('--generate-only',action='store_true');p.add_argument('--seed',type=int,default=203)
    a=p.parse_args();root=Path(a.root).resolve();contract=Path(a.openapi) if a.openapi else root/'generic-generator/compatibility/contracts/mealie.json'
    if not contract.is_file():raise ValueError('Pinned local contract not found: '+str(contract))
    digest=hashlib.sha256(contract.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
    if digest!='90e19aa713ab4ba15352627aca7dc37290f868b213eb65a3e1564f3b7a7ff292':raise ValueError('Pinned v3.28.0 contract differs; no mutation started')
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]
    run=root/'runs'/('native-f01-'+stamp);run.mkdir(parents=True);model=run/'model';source=root/'generic-generator'
    env=os.environ.copy();env['PYTHONPATH']=str(source)+os.pathsep+env.get('PYTHONPATH','')
    print('Evidence directory: '+str(run),flush=True)
    report={'status':'PREPARING','live_replay_started':False,'core_modified':False,'historical_stories_reused':False}
    try:
        corecmd=[sys.executable,'-B','-m','generator_v56','generate','--openapi',str(contract),'--output',str(run/'core-baseline/spec/js'),'--name','mealie','--base-url',a.base_url,'--seed',str(a.seed),'--story-profile','parallel-crud']
        if execute(corecmd,source,run/'core-generation-output.txt',env):raise ValueError('generator_v56 baseline generation failed; inspect core-generation-output.txt')
        compilecmd=[sys.executable,'-B',str(root/'tools/compile_native_lifecycle.py'),'--openapi',str(contract),'--profile',str(root/'profiles/mealie-native-f01.json'),'--output',str(model),'--base-url',a.base_url,'--namespace','sbt-f01-'+uuid.uuid4().hex[:16]]
        if execute(compilecmd,root,run/'compile-output.txt'):raise ValueError('Native F01 contract binding failed; inspect compile-output.txt')
        shutil.copy2(contract,run/'openapi-original.json');shutil.copy2(root/'profiles/mealie-native-f01.json',run/'policy-original.json')
        report['status']='F01_GENERATED_NOT_EXECUTED'
        report['core_baseline_generated']=True
        report['native_compiler']='optional declarative lifecycle extension'
        report['generator_core_dir']=str(source/'generator_v56')
        if a.generate_only:return
        native=['java','-Xmx1g','-jar',str(Path(a.jar).resolve())] if a.jar else ['provengo']
        # Check installed CLI options before any server request.
        subprocess.run(native+['sample','--help'],cwd=root,stdout=(run/'sample-help.txt').open('w'),stderr=subprocess.STDOUT,check=True)
        subprocess.run(native+['run','--help'],cwd=root,stdout=(run/'run-help.txt').open('w'),stderr=subprocess.STDOUT,check=True)
        sh=(run/'sample-help.txt').read_text(errors='replace');rh=(run/'run-help.txt').read_text(errors='replace')
        if '--output-file' not in sh or '--input-file' not in rh:raise ValueError('Installed native CLI flags differ; help captured, no live replay started')
        cmd=native+['--batch-mode','sample','--size','1','--output-file',str(run/'samples.json'),str(model)]
        if execute(cmd,root,run/'sample-output.txt'):raise ValueError('Native symbolic sampling failed')
        if not (run/'samples.json').is_file():raise ValueError('Sampling produced no sample')
        sample=json.loads((run/'samples.json').read_text(encoding='utf-8-sig'))
        events=[]
        def scan(v):
            if isinstance(v,dict):
                if v.get('name','').startswith('Native:'):events.append(v)
                for x in v.values():scan(x)
            elif isinstance(v,list):
                for x in v:scan(x)
        scan(sample)
        if not any(e['name']=='Native:Complete' for e in events):raise ValueError('Sample lacks Native:Complete; no replay started')
        plan=json.loads((model/'native-policy-bound.json').read_text());steps=set(plan['steps']);verified={e.get('data',{}).get('step') for e in events if e['name']=='Native:Verified'}
        if not steps.issubset(verified):raise ValueError('Not all symbolic verifiers completed; no replay started')
        # No credentials are written; wrapper supplies temporary environment values.
        report['live_replay_started']=True
        code=execute(native+['--batch-mode','run','--input-file',str(run/'samples.json'),str(model)],root,run/'live-output.txt')
        log=(run/'live-output.txt').read_text(errors='replace')
        for secret in (os.environ.get('MEALIE_ACCEPTANCE_PASSWORD'),):
            if secret:log=log.replace(secret,'<REDACTED>')
        log=re.sub(r'Bearer [A-Za-z0-9._~-]+', 'Bearer <REDACTED>', log)
        (run/'live-output.txt').write_text(log,encoding='utf-8')
        observations=[];receipts=[]
        for line in log.splitlines():
            for marker,target in [('NATIVE_QUANTITY_OBSERVATION ',observations),('NATIVE_RECEIPT ',receipts)]:
                if marker in line:
                    try:target.append(json.loads(line.split(marker,1)[1]))
                    except json.JSONDecodeError:pass
        (run/'response-receipts.json').write_text(json.dumps(receipts,indent=2));(run/'quantity-observations.json').write_text(json.dumps(observations,indent=2))
        report.update(native_exit=code,observations=len(observations))
        if 'F01_QUANTITY_CANDIDATE' in log:report['status']='F01_SEMANTIC_CANDIDATE_REQUIRES_QUALIFICATION'
        elif code==0 and len(observations)==3:report['status']='F01_NOT_REPRODUCED_IN_THIS_RUN'
        else:report['status']='F01_INCOMPLETE'
    except Exception as e:report.update(status='F01_INCOMPLETE',error=str(e))
    finally:
        if (run/'live-output.txt').is_file():
            log=(run/'live-output.txt').read_text(errors='replace')
            secret=os.environ.get('MEALIE_ACCEPTANCE_PASSWORD')
            if secret:log=log.replace(secret,'<REDACTED>')
            log=re.sub(r'Bearer [A-Za-z0-9._~-]+','Bearer <REDACTED>',log)
            (run/'live-output.txt').write_text(log,encoding='utf-8')
        (run/'acceptance-report.json').write_text(json.dumps(report,indent=2))
        with zipfile.ZipFile(run/'review.zip','w',zipfile.ZIP_DEFLATED) as z:
            for f in run.rglob('*'):
                if f.is_file() and f.name!='review.zip':z.write(f,f.relative_to(run).as_posix())
        print(report['status']);print('Review ZIP: '+str(run/'review.zip'))
    if report['status'] not in ('F01_GENERATED_NOT_EXECUTED','F01_NOT_REPRODUCED_IN_THIS_RUN'):sys.exit(1)
if __name__=='__main__':main()
