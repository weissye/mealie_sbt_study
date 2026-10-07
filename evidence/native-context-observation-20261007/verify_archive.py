"""Offline qualification and regeneration. Never sends HTTP requests."""
import hashlib, json, re, sys, tempfile, zipfile
from pathlib import Path

def verify(root):
    root = Path(root)
    manifest = json.loads((root/'checksums.json').read_text(encoding='utf-8-sig'))
    for name, expected in manifest.items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest() == expected, name
    with zipfile.ZipFile(root/'review-original.zip') as z:
        assert z.testzip() is None
        result = json.loads(z.read('result.json'))
        assert result['fixture_only'] and result['sut_requests'] == 0
        assert result['native_provengo_executed']
        assert [c['case'] for c in result['cases']] == ['control','error','changed']
        for c in result['cases']:
            mode = c['case']
            log = z.read(mode+'/native-run.log').decode('utf-8-sig')
            e = c['evidence'][0]
            assert len(c['evidence']) == 1
            expected = [('POST','/resources',201),('GET','/resources/fixture-1',200),
                        ('PATCH','/resources/fixture-1',200),('GET','/resources/fixture-1',200),
                        ('POST','/resources/fixture-1/action',200 if mode=='control' else 500),
                        ('GET','/resources/fixture-1',200)]
            assert [(r['method'],r['path'],r['status']) for r in c['fixture_requests']] == expected
            markers = [json.loads(l.split('CONTEXT_OBSERVATION_EVIDENCE ',1)[1])
                       for l in log.splitlines() if 'CONTEXT_OBSERVATION_EVIDENCE ' in l]
            assert markers == [e]
            assert e['observationsComplete'] and e['identityMatches'] and e['readbackCode']==200
            assert e['contextExpected']=={'name':'updated'} and e['revision']==2
            assert e['baseline']=={'id':'fixture-1','name':'updated'}
            assert e['readback']=={'id':'fixture-1','name':'injected-change' if mode=='changed' else 'updated'}
            assert e['expectedMatches']==(mode!='changed') and e['baselineMatches']==(mode!='changed')
            assert e['contractStatusValid']==(mode=='control')
            assert e['code']==(200 if mode=='control' else 500)
            assert 'CONTEXT_REVISION_VERIFIED revision=1' in log and 'CONTEXT_REVISION_VERIFIED revision=2' in log
            if mode=='control':
                assert c['exit_code']==0 and 'Test Result: SUCCESS' in log
            else:
                assert c['exit_code']==1 and 'Test Result: FAIL' in log
                assert log.index('CONTEXT_OBSERVATION_EVIDENCE ') < log.index('FAIL: Deferred')
            assert c['accepted']
            with tempfile.TemporaryDirectory() as temp:
                sys.path.insert(0,str(root/'source'))
                from generator_v56.render.context_observation import generate
                out=Path(temp)/'spec/js'
                wire=z.read(mode+'/spec/js/interfaces.observation.js').decode('utf-8-sig')
                base=re.search(r'http://127\.0\.0\.1:\d+',wire).group(0)
                generate(root/'source/model/fixture-openapi.json',out,base)
                for name in ['dal.js','stories.observation.js','interfaces.observation.js','generation_report.json']:
                    saved=z.read(mode+'/spec/js/'+name).decode('utf-8-sig').replace('\r\n','\n')
                    assert (out/name).read_text(encoding='utf-8').replace('\r\n','\n') == saved, (mode,name)
    print('NATIVE_CONTEXT_ARCHIVE_VERIFIED: 3 cases; 18 fixture requests; 12 regenerated files match after newline normalization; no requests sent.')

if __name__=='__main__':
    verify(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent)
