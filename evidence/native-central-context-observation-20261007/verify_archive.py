"""Offline evidence qualification and regeneration; no native execution or HTTP."""
import hashlib,io,json,re,subprocess,sys,tempfile,zipfile
from pathlib import Path
from run_native import qualify
from compile_fixture import compile_driver

def verify(root):
    root=Path(root).resolve()
    manifest=json.loads((root/'checksums.json').read_text(encoding='utf-8-sig'))
    for name,digest in manifest.items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
    with zipfile.ZipFile(root/'review-original.zip') as z:
        assert z.testzip() is None
        summary=json.loads(z.read('result.json'))
        assert summary['fixture_only'] and summary['sut_requests']==0 and summary['native_provengo_executed']
        assert [c['case'] for c in summary['cases']]==['control','error','changed']
        assert summary['status']=='CENTRAL_NATIVE_OBSERVATION_ACCEPTANCE_PASS'
        total=0
        with tempfile.TemporaryDirectory() as temp:
            compiler=Path(temp)/'compiler';compiler.mkdir()
            with zipfile.ZipFile(io.BytesIO(z.read('generator-source.zip'))) as source:
                assert source.testzip() is None
                for info in source.infolist():
                    destination=(compiler/info.filename).resolve()
                    if not destination.is_relative_to(compiler.resolve()):raise ValueError('Unsafe source archive path')
                    if not info.is_dir():
                        destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(source.read(info))
            for case in summary['cases']:
                mode=case['case'];log=z.read(mode+'/native-run.log').decode('utf-8-sig')
                accepted,evidence,models,reasons=qualify(mode,case['exit_code'],log,case['fixture_requests'])
                assert accepted,reasons
                assert evidence==case['evidence'] and models==case['model'] and case['accepted']
                total+=len(case['fixture_requests'])
                report=json.loads(z.read(mode+'/spec/js/fixture-driver-provenance.json'))
                for path,digest in report['generator_source_sha256'].items():
                    assert hashlib.sha256((compiler/path).read_bytes()).hexdigest()==digest,path
                wire=z.read(mode+'/spec/js/interfaces.fixture.js').decode('utf-8-sig')
                base=re.search(r'http://127\.0\.0\.1:\d+',wire).group(0)
                out=Path(temp)/mode/'spec/js'
                cmd=[sys.executable,'-B','-m','generator_v56','context-generate','--openapi',str(root/'fixture-openapi.json'),'--output',str(out),'--name','fixture','--base-url',base,'--resource','/resources','--instances-per-entity','1','--seed','20261007','--observation-support']
                subprocess.run(cmd,cwd=compiler,check=True,capture_output=True)
                compile_driver(compiler,root/'fixture-openapi.json',out)
                for name in ['interfaces.fixture.js','stories.fixture.js','dal.js','generation_report.json','fixture-driver-provenance.json']:
                    observed=z.read(mode+'/spec/js/'+name).decode('utf-8-sig').replace('\r\n','\n')
                    assert (out/name).read_text(encoding='utf-8').replace('\r\n','\n')==observed,(mode,name)
                config=z.read(mode+'/config/provengo.yml').decode('utf-8-sig').replace('\r\n','\n')
                assert (out.parent.parent/'config/provengo.yml').read_text()==config
        assert total==21
    print('CENTRAL_NATIVE_ARCHIVE_VERIFIED: 3 accepted native cases; 21 fixture responses; 15 regenerated JS/report files and 3 configs match; no HTTP or native execution.')

if __name__=='__main__':verify(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent)
