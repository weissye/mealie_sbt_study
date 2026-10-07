import hashlib,io,json,subprocess,sys,tempfile,zipfile,importlib.util
from pathlib import Path
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent
for name,expected in json.loads((root/'checksums.json').read_text()).items():
 if hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:raise SystemExit('Checksum mismatch: '+name)
z=zipfile.ZipFile(root/'review-original.zip');assert z.testzip() is None
source=zipfile.ZipFile(io.BytesIO(z.read('generator-source.zip')));assert source.testzip() is None
assert (root/'generator-source.zip').read_bytes()==z.read('generator-source.zip')
sys.path.insert(0,str(root.resolve()))
from run_native import qualify
result=json.loads(z.read('result.json'));assert result['status']=='CENTRAL_PROCESS_BINDING_ACCEPTANCE_PASS'
assert result['fixture_only'] and result['sut_requests']==0 and result['native_provengo_executed']
assert [c['case'] for c in result['cases']]==['control','error','changed']
with tempfile.TemporaryDirectory() as d:
 r=Path(d);compiler=r/'compiler';compiler.mkdir()
 for name in source.namelist():
  path=(compiler/name).resolve()
  if not path.is_relative_to(compiler.resolve()):raise SystemExit('Unsafe source path')
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(source.read(name))
 contract=r/'fixture.json';contract.write_bytes(z.read('fixture-openapi.json'))
 for case in result['cases']:
  mode=case['case'];log=z.read(mode+'/native-run.log').decode('utf-8-sig')
  ok,_,_,reasons=qualify(mode,case['exit_code'],log,case['fixture_requests']);assert ok,reasons
  import re
  interface=z.read(mode+'/spec/js/interfaces.fixture.js').decode('utf-8-sig')
  base=json.loads(re.search(r'new RESTSession\(("[^"]+")',interface).group(1))
  out=r/mode/'spec/js'
  subprocess.run([sys.executable,'-B','-m','generator_v56','context-generate','--openapi',str(contract),'--output',str(out),'--name','fixture','--base-url',base,'--resource','/resources','--instances-per-entity','1','--seed','20261007','--observed-action','POST:/resources/{id}/action'],cwd=compiler,capture_output=True,check=True)
  for name in ['stories.fixture.js','interfaces.fixture.js','dal.js','generation_report.json']:
   actual=(out/name).read_bytes().replace(b'\r\n',b'\n')
   executed=(root/'executed'/mode/'spec/js'/name).read_bytes().replace(b'\r\n',b'\n')
   assert actual==executed==z.read(mode+'/spec/js/'+name).replace(b'\r\n',b'\n'),(mode,name)
  assert (r/mode/'config/provengo.yml').read_bytes().replace(b'\r\n',b'\n')==z.read(mode+'/config/provengo.yml').replace(b'\r\n',b'\n')
print('CENTRAL_PROCESS_ARCHIVE_VERIFIED: 3 native cases; 21 fixture responses; 12 generated files and 3 configs match. No HTTP or native execution.')
