"""Archive exact accepted files plus credential-free parsed observation evidence.
Raw native logs stay local. This tool never calls the SUT or runs Provengo.
"""
import argparse,hashlib,json,re,subprocess,sys,tempfile,zipfile,shutil
from pathlib import Path
from native_log_text import decode_native_log
parser=argparse.ArgumentParser();parser.add_argument('--package',required=True);parser.add_argument('--repository',required=True);parser.add_argument('--accepted-project',required=True);args=parser.parse_args()
package=Path(args.package).resolve();repository=Path(args.repository).resolve();accepted=Path(args.accepted_project).resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def lf(p):return p.read_bytes().replace(b'\r\n',b'\n')
if not (repository/'.git').exists():raise SystemExit('Target is not a Git checkout')
proof=package/'evidence/native-context-accepted-20261006';qual=json.loads((proof/'qualification.json').read_text())
archive=proof/'generator-original.zip'
if sha(archive)!=qual['generator_archive_sha256']:raise SystemExit('Frozen generator archive changed')
report=json.loads((accepted/'spec/js/generation_report.json').read_text())
if report['seed']!=qual['seed'] or report['source_sha256']!=qual['contract_sha256']:raise SystemExit('Wrong accepted project seed/contract')
log=accepted/'native-run.log'
text=decode_native_log(log.read_bytes())
if 'Test Result: SUCCESS' not in text or re.search(r'Test Result: (?:ERROR|FAIL)',text):raise SystemExit('Accepted log does not confirm native success')
with tempfile.TemporaryDirectory() as tmp:
 base=Path(tmp)/'base'
 with zipfile.ZipFile(archive) as z:
  for entry in z.namelist():
   if Path(entry).is_absolute() or '..' in Path(entry).parts:raise SystemExit('Unsafe frozen archive path')
  z.extractall(base)
 out=Path(tmp)/'regenerated/spec/js'
 command=[sys.executable,'-B','-m','generator_v56','context-generate','--openapi',str(base/'model/mealie-openapi.v3.28.0.json'),'--output',str(out),'--name','mealie','--base-url','http://127.0.0.1:9925','--instances-per-entity','1','--seed',str(qual['seed'])]
 for path in report['scope_paths']:command+=['--resource',path]
 subprocess.run(command,cwd=base,check=True,stdout=subprocess.DEVNULL)
 for name in ('stories.mealie.js','interfaces.mealie.js','dal.js'):
  if lf(out/name)!=lf(accepted/'spec/js'/name):raise SystemExit('Accepted generated source differs from frozen generator: '+name)
# Check that the local run has the same stable observations as the reviewed transcript.
snapshots=[];verified=[]
for line in text.splitlines():
 match=re.search(r"RTV: setting '(SNAPSHOT_[^']+)' to '(.*)'$",line)
 if match:snapshots.append({'key':match[1],'response':json.loads(match[2])})
 match=re.search(r'Selected: \[ModelVerified \{logicalId:"([^"]+)", revision:([\d.]+)\}',line)
 if match:verified.append({'logicalId':match[1],'revision':float(match[2])})
if snapshots!=qual['independent_snapshots'] or verified!=qual['verified']:raise SystemExit('Local accepted observations differ from reviewed evidence')
# Build a reviewed immutable tree without runtime directories, databases or raw logs.
with tempfile.TemporaryDirectory() as tmp:
 staged=Path(tmp)/'archive';staged.mkdir()
 (staged/'.gitattributes').write_text('*.py text eol=lf\n*.js text eol=lf\n*.json text eol=lf\n*.md text eol=lf\n*.yml text eol=lf\n*.ps1 text eol=lf\n*.zip binary\n')
 for directory in ('generator_v56','model','scripts','tests','tools','evidence','preview-f01'):
  for source in (package/directory).rglob('*'):
   if not source.is_file() or '__pycache__' in source.parts or source.suffix=='.pyc':continue
   relative=source.relative_to(package);dest=staged/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
 for name in ('README-F01.md','F01-VALIDATION.json'):
  source=package/name;shutil.copyfile(source,staged/name)
 for source in (accepted/'spec/js').glob('*'):
  if source.suffix not in ('.js','.json'):continue
  dest=staged/'evidence/native-context-accepted-20261006/accepted-project/spec/js'/source.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
 dest=staged/'evidence/native-context-accepted-20261006/accepted-project/config/provengo.yml';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(accepted/'config/provengo.yml',dest)
 (staged/'evidence/native-context-accepted-20261006/local-log-provenance.json').write_text(json.dumps({'raw_log_sha256':sha(log),'raw_log_archived':False,'observations_match_reviewed_transcript':True},indent=2))
 manifest={p.relative_to(staged).as_posix():sha(p) for p in sorted(staged.rglob('*')) if p.is_file()}
 (staged/'ARCHIVE-SHA256.json').write_text(json.dumps(manifest,indent=2))
 target=repository/'research/native-context-f01-20261006'
 if target.exists():
  for source in staged.rglob('*'):
   if source.is_file() and (not (target/source.relative_to(staged)).is_file() or (target/source.relative_to(staged)).read_bytes()!=source.read_bytes()):raise SystemExit('Existing checkpoint differs; nothing overwritten')
 else:shutil.copytree(staged,target)
 print('ACCEPTED_CONTEXT_AND_F01_SOURCE_ARCHIVED: '+str(target))
 print('No SUT requests. Original raw log retained locally. Commit/push is performed by the PowerShell wrapper.')
