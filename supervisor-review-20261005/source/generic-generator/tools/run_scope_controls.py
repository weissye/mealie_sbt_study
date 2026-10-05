"""Generate and execute identity programs; every HTTP request is native Provengo."""
import argparse,json,os,secrets,sys,subprocess,zipfile,hashlib
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from generator_v56.pipeline import run_pipeline
from tools.relationship_execution import native,redact,find_receipt,audit_samples,model_hashes
from tools.identity_receipts import validate_identity_receipts,IdentityMismatch
from tools.check_route_server import check
from tools.identity_credentials import save_fixture_credentials


def write(path,value):path.write_text(json.dumps(redact(value),indent=2)+'\n',encoding='utf-8')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def run(root,base,seed):
 started=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
 generator=root/'generic-generator';review=Path.home()/'Downloads'/('mealie-scope-controls-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f'));review.mkdir(parents=True)
 summary=[];saved={k:os.environ.get(k) for k in ('SBT_IDP_A_PASSWORD','SBT_IDP_B_PASSWORD')};result_code=0
 try:
  if not os.environ.get('SBT_REL_USERNAME') or not os.environ.get('SBT_REL_PASSWORD'):raise ValueError('Provisioning account credentials are required.')
  check(root,base,review)
  write(review/'campaign-config.json',dict(seed=seed,server=base,scope='foreign versus absent recipe references; shared group and separate households',automatic_retry=False,reset_replay_accepted=False))
  for case in ('reference-controls','household-controls'):
   case_dir=review/case;case_dir.mkdir();runtime=json.loads((generator/f'profiles/mealie-{case}-runtime.json').read_text(encoding='utf-8-sig'));scope=json.loads((generator/f'profiles/mealie-{case}-scope.json').read_text(encoding='utf-8-sig'))
   output=run_pipeline(str(generator/'compatibility/contracts/mealie.json'),'mealie',base,seed,story_profile='parallel-crud',compile_relationship_model=True,relationship_profile=scope,relationship_runtime=runtime)
   project=root/'provengo'/('identity-'+case+'-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f'));(project/'spec/js').mkdir(parents=True);(project/'config').mkdir();(project/'config/provengo.yml').write_text('version: 2\n');(project/'spec/js/interfaces.mealie.js').write_text(output.interfaces_js,encoding='utf-8');(project/'spec/js/stories.mealie.js').write_text(output.stories_js,encoding='utf-8')
   for name,data in output.resource_maps.items():write(project/(name+'.json'),data)
   write(project/'generation_report.json',output.generation_report);write(project/'dependency_graph.json',output.dependency_graph_report)
   sampled=native(['sample','--algorithm','random','--size','2','--max-length','400','-o','relationship-samples.json'],project);(case_dir/'sample-output.txt').write_text(redact(sampled.stdout+sampled.stderr),encoding='utf-8')
   samples_path=project/'relationship-samples.json'
   if sampled.returncode or not samples_path.exists():raise ValueError('Native identity sampling did not produce a sample.')
   if samples_path.stat().st_size>4*1024**2:raise ValueError('Identity sample exceeds the tested 4 MiB bound.')
   audit=audit_samples(json.loads(samples_path.read_text()),output.resource_maps['relationship_scenario_plan']);audit.update(samples_sha256=sha(samples_path),model_sha256=model_hashes(project));write(case_dir/'sample-acceptance.json',audit)
   for sample_id in (1,2):
    for k in saved:os.environ[k]=secrets.token_urlsafe(24)
    # Replaying a second schedule intentionally creates fresh groups, users and resources.
    print(f'Campaign {case}; sample {sample_id}: new regular users and owned resources.',flush=True)
    if sha(samples_path)!=audit['samples_sha256'] or model_hashes(project)!=audit['model_sha256']:raise ValueError('Model or samples changed after the symbolic audit.')
    executed=native(['--batch-mode','run','--run-source',str(samples_path),'--run-id',str(sample_id)],project);output_text=executed.stdout+'\n'+executed.stderr
    receipt=find_receipt(output_text);status=dict(case=case,sample=sample_id,project=str(project),native_exit=executed.returncode,status='INCONCLUSIVE',new_bug_confirmed=False)
    if executed.returncode==0 and receipt:
     status['runtime_receipt']=receipt
     try:status['local_credentials']=save_fixture_credentials(receipt,review.name,case,sample_id)
     except OSError as e:status['credential_preservation_error']=str(e)
     try:
      if case=='reference-controls' and any(receipt['identity_program']['observations']['missing_read_'+a]['code']!=404 for a in ('a','b')):raise ValueError('Absent-recipe control could not establish absence.')
      status['qualification']=validate_identity_receipts(receipt,output.resource_maps['relationship_scenario_plan']);status['status']='PASS'
     except IdentityMismatch as e:status.update(status='IDENTITY_CANDIDATE',error=str(e))
     except ValueError as e:status.update(status='INCONCLUSIVE',error=str(e))
    elif executed.returncode:status['error']='Native execution failed; inspect scrubbed output.'
    else:status['error']='Complete runtime receipt was not observed.'
    write(case_dir/f'result-{sample_id}.json',status);(case_dir/f'run-output-{sample_id}.txt').write_text(redact(output_text),encoding='utf-8')
    live=case_dir/f'live-{sample_id}.zip'
    with zipfile.ZipFile(live,'w',zipfile.ZIP_DEFLATED) as z:
     z.write(case_dir/f'result-{sample_id}.json','run-acceptance.json');z.write(case_dir/f'run-output-{sample_id}.txt','run-output.txt')
     for path in (project/'relationship_scenario_plan.json',project/'relationship_compilation.json',project/'generation_report.json',project/'dependency_graph.json',samples_path):z.write(path,path.name)
     for path in (project/'spec/js').glob('*.js'):z.write(path,'spec/js/'+path.name)
    summary.append(dict(case=case,sample=sample_id,status=status['status'],sha256=sha(live),review=str(live)))
    print(status['status'],flush=True)
    if status['status']=='INCONCLUSIVE':raise ValueError('Identity campaign stopped at infrastructure/setup failure. Evidence retained.')
 except (ValueError,OSError,subprocess.TimeoutExpired) as e:
  result_code=1;write(review/'campaign-error.json',dict(error=str(e)));print('IDENTITY_CAMPAIGN_NOT_ACCEPTED: '+str(e),flush=True)
 finally:
  write(review/'campaign-summary.json',dict(runs=summary,new_bug_count_confirmed=False,reset_replay_accepted=False,automatic_deletion=False,automatic_retry=False))
  # Read-only exception evidence; a missing Docker client never changes a run verdict.
  if any(r['status']=='IDENTITY_CANDIDATE' for r in summary):
   try:
    logs=subprocess.run(['docker','logs','--timestamps','--since',started,'--tail','2000',os.environ.get('MEALIE_STUDY_CONTAINER','mealie-sbt-study-mealie-1')],capture_output=True,text=True,timeout=15)
    (review/'server-logs.txt').write_text(redact(logs.stdout+'\n'+logs.stderr),encoding='utf-8')
    write(review/'server-logs-status.json',dict(status='CAPTURED' if logs.returncode==0 else 'UNAVAILABLE',exit_code=logs.returncode,since=started))
   except (OSError,subprocess.TimeoutExpired) as error:
    write(review/'server-logs-status.json',dict(status='UNAVAILABLE',error_type=type(error).__name__,since=started))
  for k,v in saved.items():
   if v is None:os.environ.pop(k,None)
   else:os.environ[k]=v
  archive=review/'campaign.zip'
  with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
   for p in sorted(review.rglob('*')):
    if p.is_file() and p!=archive:z.write(p,p.relative_to(review).as_posix())
  print('Review ZIP: '+str(archive),flush=True)
 return result_code

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--base-url',default='http://127.0.0.1:9925');p.add_argument('--seed',type=int,default=721);a=p.parse_args();raise SystemExit(run(a.root.resolve(),a.base_url,a.seed))
