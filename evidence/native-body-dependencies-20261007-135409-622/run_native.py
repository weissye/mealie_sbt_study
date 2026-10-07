import argparse,json,shutil,subprocess,sys,threading,zipfile
from pathlib import Path
from datetime import datetime
from http.server import ThreadingHTTPServer
from fixture_server import Fixture
from qualification import qualify

def main():
 p=argparse.ArgumentParser();p.add_argument('--generator-root',type=Path,required=True);p.add_argument('--generate-only',action='store_true');a=p.parse_args()
 compiler=a.generator_root.resolve();package=Path(__file__).resolve().parent
 runner=shutil.which('provengo') or shutil.which('provengo.bat')
 if not a.generate_only and not runner:raise SystemExit('Provengo not found on PATH')
 run=compiler/'runs'/('native-body-dependencies-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'));run.mkdir(parents=True)
 for name in ['fixture-openapi.json','fixture_server.py','qualification.py','run_native.py','verify_archive.py','test_wire_expression.js']:shutil.copyfile(package/name,run/name)
 server=ThreadingHTTPServer(('127.0.0.1',0),Fixture);server.states={};server.receipts=[]
 thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();cases=[]
 print('Evidence directory:',run,flush=True)
 try:
  if not a.generate_only:
   v=subprocess.run([runner,'--version'],capture_output=True,text=True,errors='replace',timeout=30);(run/'provengo-version.txt').write_text(v.stdout+v.stderr,encoding='utf-8')
  for mode in ['control','error','changed']:
   server.mode=mode;server.states={};server.receipts=[];project=run/mode;js=project/'spec/js'
   cmd=[sys.executable,'-B','-m','generator_v56','context-generate','--openapi',str(package/'fixture-openapi.json'),'--output',str(js),'--name','fixture','--base-url','http://127.0.0.1:'+str(server.server_port),'--resource','/resources','--resource','/foods','--resource','/units','--instances-per-entity','1','--seed','20261007','--observed-action','POST:/resources/{id}/action']
   generated=subprocess.run(cmd,cwd=compiler,capture_output=True,text=True,errors='replace');(run/(mode+'-generation.log')).write_text(generated.stdout+generated.stderr,encoding='utf-8')
   if generated.returncode:raise RuntimeError('Central generation failed; inspect generation log')
   for f in js.glob('*.js'):subprocess.run(['node','--check',str(f)],check=True,capture_output=True)
   subprocess.run(['node',str(package/'test_wire_expression.js'),str(js/'interfaces.fixture.js')],check=True)
   print('Stories:',js/'stories.fixture.js',flush=True);print('Interfaces:',js/'interfaces.fixture.js',flush=True)
   if a.generate_only:continue
   print('Running isolated native fixture:',mode,flush=True)
   try:
    native=subprocess.run([runner,'run',str(project)],capture_output=True,text=True,errors='replace',timeout=90);code=native.returncode;log=native.stdout+'\n'+native.stderr
   except subprocess.TimeoutExpired as timeout:code=None;log='NATIVE_TIMEOUT\n'+str(timeout.stdout or '')+'\n'+str(timeout.stderr or '')
   (project/'native-run.log').write_text(log,encoding='utf-8')
   accepted,reasons=qualify(mode,code,log,server.receipts)
   cases.append({'case':mode,'accepted':accepted,'exit_code':code,'fixture_requests':server.receipts[:],'reasons':reasons})
   print('CASE '+mode+': '+('ACCEPTED' if accepted else 'NOT_ACCEPTED'),flush=True)
   if not accepted:print('Reasons:',reasons,flush=True);break
 finally:
  server.shutdown();server.server_close();thread.join(timeout=5)
  accepted=len(cases)==3 and all(c['accepted'] for c in cases)
  status='BODY_DEPENDENCIES_GENERATED_NOT_EXECUTED' if a.generate_only else 'NATIVE_BODY_DEPENDENCIES_ACCEPTANCE_PASS' if accepted else 'NATIVE_BODY_DEPENDENCIES_NOT_ACCEPTED'
  (run/'result.json').write_text(json.dumps({'status':status,'fixture_only':True,'sut_requests':0,'native_provengo_executed':bool(cases),'cases':cases},indent=2),encoding='utf-8')
  with zipfile.ZipFile(run/'generator-source.zip','w',zipfile.ZIP_DEFLATED) as z:
   for f in sorted((compiler/'generator_v56').rglob('*.py')):z.write(f,str(f.relative_to(compiler)))
  with zipfile.ZipFile(run/'review.zip','w',zipfile.ZIP_DEFLATED) as z:
   for f in sorted(run.rglob('*')):
    if f.is_file() and f.name!='review.zip':z.write(f,str(f.relative_to(run)))
  print(status,flush=True);print('Review ZIP:',run/'review.zip',flush=True)
 if not a.generate_only and not accepted:raise SystemExit(1)
 (package/'last-review-path.txt').write_text(str(run/'review.zip'),encoding='utf-8')
if __name__=='__main__':main()
