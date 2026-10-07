"""Native central Context helper acceptance against an isolated local HTTP fixture."""
import argparse,json,shutil,subprocess,sys,threading,zipfile,hashlib
from pathlib import Path
from datetime import datetime
from http.server import ThreadingHTTPServer
from fixture_server import Fixture


def qualify(mode,code,log,receipts):
    marker='OBSERVATION_EVIDENCE '
    evidence=[json.loads(line.split(marker,1)[1]) for line in log.splitlines() if marker in line]
    models=[json.loads(line.split('OBSERVATION_MODEL ',1)[1]) for line in log.splitlines() if 'OBSERVATION_MODEL ' in line]
    expected=[('POST','/resources',201),('GET','/resources/fixture-1',200),('GET','/resources/fixture-1',200),('PATCH','/resources/fixture-1',200),('GET','/resources/fixture-1',200),('POST','/resources/fixture-1/action',200 if mode=='control' else 500),('GET','/resources/fixture-1',200)]
    reasons=[]
    if [(r['method'],r['path'],r['status']) for r in receipts]!=expected:reasons.append('HTTP sequence differs')
    if len(evidence)!=1 or len(models)!=1:reasons.append('Missing or repeated evidence/model marker')
    if reasons:return False,evidence,models,reasons
    e=evidence[0];model=models[0];reads=e.get('readbacks',[])
    if not e.get('captureComplete') or not e.get('observationsComplete'):reasons.append('Observation incomplete')
    if e.get('code')!=(200 if mode=='control' else 500):reasons.append('Incorrect captured status')
    if e.get('contractStatusValid')!=(mode=='control'):reasons.append('Incorrect contract classification')
    if len(reads)!=1:reasons.append('Wrong readback count')
    else:
        r=reads[0]
        if not r.get('identityMatches') or not r.get('usable') or r.get('code')!=200:reasons.append('Readback unusable')
        if r.get('expectedMatches')!=(mode!='changed'):reasons.append('Incorrect expected-state comparison')
        if r.get('actual')!=receipts[-1]['state']:reasons.append('Callback and fixture state differ')
    if model!={'name':receipts[4]['state']['name']}:reasons.append('DAL does not match verified pre-action state')
    expected_actual=dict(receipts[4]['state'])
    if mode=='changed':expected_actual['name']='injected-change'
    if receipts[-1]['state']!=expected_actual:reasons.append('Unexpected final fixture state')
    if mode=='control':
        if code!=0 or not any('Test Result: '+s in log for s in ['SUCCESS','PASS']):reasons.append('Control did not succeed')
    else:
        failure='FAIL: Observation incomplete or contract failure after readbacks'
        if code!=1 or 'Test Result: FAIL' not in log or failure not in log:reasons.append('Expected deferred failure absent')
        elif log.index(marker)>log.index(failure):reasons.append('Failure preceded evidence')
    return not reasons,evidence,models,reasons


def main():
    p=argparse.ArgumentParser();p.add_argument('--generator-root',type=Path,required=True);p.add_argument('--generate-only',action='store_true');a=p.parse_args()
    compiler=a.generator_root.resolve();package=Path(__file__).resolve().parent
    if not (compiler/'generator_v56/render/context_observation_common.py').is_file():raise SystemExit('Integrated observation support not found')
    runner=shutil.which('provengo') or shutil.which('provengo.bat')
    if not a.generate_only and not runner:raise SystemExit('Provengo not found on PATH')
    run=compiler/'runs'/('central-native-observation-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));run.mkdir(parents=True)
    for name in ['fixture-openapi.json','fixture_server.py','run_native.py']:shutil.copyfile(package/name,run/name)
    server=ThreadingHTTPServer(('127.0.0.1',0),Fixture);server.receipts=[];server.resource=None
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();cases=[]
    print('Evidence directory:',run,flush=True)
    try:
        if not a.generate_only:
            v=subprocess.run([runner,'--version'],capture_output=True,text=True,errors='replace',timeout=30)
            (run/'provengo-version.txt').write_text(v.stdout+v.stderr,encoding='utf-8')
        for mode in ['control','error','changed']:
            server.mode=mode;server.receipts=[];server.resource=None;project=run/mode;js=project/'spec/js'
            cmd=[sys.executable,'-B','-m','generator_v56','context-generate','--openapi',str((package/'fixture-openapi.json').resolve()),'--output',str(js),'--name','fixture','--base-url','http://127.0.0.1:'+str(server.server_port),'--resource','/resources','--instances-per-entity','1','--seed','20261007','--observed-action','POST:/resources/{id}/action']
            generation=subprocess.run(cmd,cwd=compiler,capture_output=True,text=True,errors='replace')
            (run/(mode+'-generation.log')).write_text(generation.stdout+generation.stderr,encoding='utf-8')
            if generation.returncode:raise RuntimeError('Central CLI generation failed; see generation log')
            for f in js.glob('*.js'):subprocess.run(['node','--check',str(f)],check=True,capture_output=True)
            print('Stories:',js/'stories.fixture.js',flush=True);print('Interfaces:',js/'interfaces.fixture.js',flush=True)
            if a.generate_only:continue
            print('Running local fixture case:',mode,flush=True)
            try:
                native=subprocess.run([runner,'run',str(project)],capture_output=True,text=True,errors='replace',timeout=90)
                code=native.returncode;log=native.stdout+'\n'+native.stderr
            except subprocess.TimeoutExpired as timeout:
                code=None;log='NATIVE_TIMEOUT\n'+str(timeout.stdout or '')+'\n'+str(timeout.stderr or '')
            (project/'native-run.log').write_text(log,encoding='utf-8')
            accepted,evidence,models,reasons=qualify(mode,code,log,server.receipts)
            cases.append({'case':mode,'accepted':accepted,'exit_code':code,'fixture_requests':server.receipts[:],'evidence':evidence,'model':models,'reasons':reasons})
            print('CASE '+mode+': '+('ACCEPTED' if accepted else 'NOT_ACCEPTED'),flush=True)
            if not accepted:break
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)
        accepted=len(cases)==3 and all(c['accepted'] for c in cases)
        status='GENERATED_NOT_EXECUTED' if a.generate_only else 'CENTRAL_PROCESS_BINDING_ACCEPTANCE_PASS' if accepted else 'CENTRAL_PROCESS_BINDING_NOT_ACCEPTED'
        (run/'result.json').write_text(json.dumps({'status':status,'fixture_only':True,'sut_requests':0,'native_provengo_executed':bool(cases),'cases':cases},indent=2),encoding='utf-8')
        with zipfile.ZipFile(run/'generator-source.zip','w',zipfile.ZIP_DEFLATED) as z:
            for f in sorted((compiler/'generator_v56').rglob('*.py')):
                if '__pycache__' not in f.parts:z.write(f,str(f.relative_to(compiler)))
        with zipfile.ZipFile(run/'review.zip','w',zipfile.ZIP_DEFLATED) as z:
            for f in sorted(run.rglob('*')):
                if f.is_file() and f.name!='review.zip':z.write(f,str(f.relative_to(run)))
        print(status,flush=True);print('Review ZIP:',run/'review.zip',flush=True)
    if not a.generate_only and not accepted:raise SystemExit(1)

if __name__=='__main__':main()
