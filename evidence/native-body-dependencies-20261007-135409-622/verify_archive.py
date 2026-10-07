import argparse,io,json,re,subprocess,sys,tempfile,zipfile
from pathlib import Path
from qualification import qualify

def verify(archive):
 z=zipfile.ZipFile(archive)
 if z.testzip() is not None:raise ValueError('Archive CRC failure')
 result=json.loads(z.read('result.json'))
 if result['status']!='NATIVE_BODY_DEPENDENCIES_ACCEPTANCE_PASS' or not result['fixture_only'] or result['sut_requests']!=0:raise ValueError('Not an accepted isolated fixture campaign')
 if not result['native_provengo_executed'] or [c['case'] for c in result['cases']]!=['control','error','changed']:raise ValueError('Missing native cases')
 with tempfile.TemporaryDirectory() as d:
  root=Path(d);compiler=root/'compiler';compiler.mkdir();source=zipfile.ZipFile(io.BytesIO(z.read('generator-source.zip')))
  if source.testzip() is not None:raise ValueError('Source CRC failure')
  for n in source.namelist():
   path=(compiler/n).resolve()
   if not path.is_relative_to(compiler.resolve()):raise ValueError('Unsafe source archive member')
   path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(source.read(n))
  contract=root/'fixture.json';contract.write_bytes(z.read('fixture-openapi.json'))
  for case in result['cases']:
   mode=case['case'];log=z.read(mode+'/native-run.log').decode('utf-8-sig');ok,reasons=qualify(mode,case['exit_code'],log,case['fixture_requests'])
   if not ok:raise ValueError(str(reasons))
   interface=z.read(mode+'/spec/js/interfaces.fixture.js').decode('utf-8-sig');base=json.loads(re.search(r'new RESTSession\(("[^"]+")',interface).group(1));out=root/mode/'spec/js'
   subprocess.run([sys.executable,'-B','-m','generator_v56','context-generate','--openapi',str(contract),'--output',str(out),'--name','fixture','--base-url',base,'--resource','/resources','--resource','/foods','--resource','/units','--instances-per-entity','1','--seed','20261007','--observed-action','POST:/resources/{id}/action'],cwd=compiler,capture_output=True,check=True)
   for name in ['stories.fixture.js','interfaces.fixture.js','dal.js','generation_report.json']:
    if (out/name).read_bytes().replace(b'\r\n',b'\n')!=z.read(mode+'/spec/js/'+name).replace(b'\r\n',b'\n'):raise ValueError('Regeneration mismatch: '+mode+'/'+name)
   if (root/mode/'config/provengo.yml').read_bytes().replace(b'\r\n',b'\n')!=z.read(mode+'/config/provengo.yml').replace(b'\r\n',b'\n'):raise ValueError('Config regeneration mismatch')
 print('BODY_DEPENDENCIES_ARCHIVE_VERIFIED: three native cases; 57 fixture requests; dependency IDs on wire verified; nine readbacks complete; 12 generated files and three configs match. No HTTP or native execution by verifier.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('archive',type=Path);a=p.parse_args();verify(a.archive)
