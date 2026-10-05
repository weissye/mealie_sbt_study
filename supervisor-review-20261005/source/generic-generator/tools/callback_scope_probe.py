"""Bounded native Rhino serialization probe; only GET the public contract."""
import argparse
import base64
import json
from pathlib import Path
import sys
import zipfile
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.relationship_execution import native, redact, write


def model_source(base_url, strategy="inside"):
    callbacks = [
        "if(response.code!==200)throw new Error('Probe HTTP status');var body=JSON.parse(response.body);if(!body.info||!body.info.title)throw new Error('Contract title missing');pvg.rtv.set('sbt_scope_probe_title',body.info.title);pvg.success('SBT_SCOPE_PROBE_FIRST_PASS');",
        "if(response.code!==200)throw new Error('Probe HTTP status');var body=JSON.parse(response.body);if(pvg.rtv.get('sbt_scope_probe_title')!==body.info.title)throw new Error('RTV continuity failed');pvg.success('SBT_SCOPE_PROBE_NATIVE_PASS');"
    ]
    return '\n'.join([
        '// @provengo summon rest', '// @provengo summon rtv',
        '// Deliberately large unrelated global: isolated callbacks must not capture it.',
        "var sbtScopeSentinel=Array(1001).join('GLOBAL_SCOPE_SENTINEL:');",
        'var svc=new RESTSession('+json.dumps(base_url.rstrip('/'))+');',
        callback_factory(strategy),
        'bp.log.info("SCOPE_STAGE: model loaded");',
        ('var preparedCallbacks=['+','.join('isolatedCallback('+json.dumps(c)+')' for c in callbacks)+'];' if strategy=='outside' else ''),
        'bthread("scope-probe",function(){bp.log.info("SCOPE_STAGE: bthread entered");'+''.join(
            'bp.log.info("SCOPE_STAGE: before GET '+str(i)+'");svc.get("/openapi.json",{expectedResponseCodes:[200],callback:'+('preparedCallbacks['+str(i)+']' if strategy=='outside' else 'isolatedCallback('+json.dumps(c)+')')+'});'
            for i,c in enumerate(callbacks))+'sync({request:Event("SBT:ScopeProbeComplete")});});'
    ])+'\n'


def callback_factory(strategy):
    if strategy == "baseline":
        return 'function isolatedCallback(source){bp.log.info("SCOPE_STAGE: ordinary callback");return new Function("response",source);}'
    if strategy not in {"inside", "outside"}:
        raise ValueError("Unknown callback strategy")
    return 'function isolatedCallback(source){bp.log.info("SCOPE_STAGE: context");var cx=Packages.org.mozilla.javascript.Context.getCurrentContext();bp.log.info("SCOPE_STAGE: standard scope");var scope=cx.initStandardObjects();bp.log.info("SCOPE_STAGE: compile");var fn=cx.compileFunction(scope,"function(response){"+source+"}","isolated-scope-probe",1,null);bp.log.info("SCOPE_STAGE: compiled");return fn;}'


def inspect_sample(path, require_isolation=True):
    if path.stat().st_size > 4*1024*1024:
        raise ValueError('Probe sample exceeds 4 MiB; live probe was not started.')
    samples=json.loads(path.read_text(encoding='utf-8-sig'))
    if len(samples)!=1 or not isinstance(samples[0],list):
        raise ValueError('Unexpected native sample format.')
    events=samples[0]
    calls=[e for e in events if (e.get('data') or {}).get('lib')=='REST']
    if len(calls)!=2 or not any(e.get('name')=='SBT:ScopeProbeComplete' for e in events):
        raise ValueError('Probe schedule is incomplete.')
    sizes=[]
    for event in calls:
        data=event['data']
        if data.get('method')!='GET' or not data.get('url','').endswith('/openapi.json'):
            raise ValueError('Probe contains an unauthorized operation.')
        callback=data.get('callback',{})
        if not isinstance(callback,dict) or callback.get('class')!='org.mozilla.javascript.InterpretedFunction':
            raise ValueError('Expected native Rhino callback serialization.')
        decoded=base64.b64decode(callback['object'],validate=True)
        if require_isolation and (b'GLOBAL_SCOPE_SENTINEL:' in decoded or b'sbtScopeSentinel' in decoded):
            raise ValueError('Isolated callback still captures unrelated global state.')
        sizes.append(len(decoded))
    return sizes


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--base-url',default='http://127.0.0.1:9925');parser.add_argument('--review-zip',required=True)
    args=parser.parse_args();root=Path(args.root);project=root/'provengo'/('callback-scope-probe-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    (project/'spec/js').mkdir(parents=True);(project/'config').mkdir();(project/'config/provengo.yml').write_text('version: 2\n')
    status={'status':'SCOPE_PROBE_NOT_ACCEPTED','resource_mutations':0,'automatic_retry':False,'variants':[]};code=1
    try:
        accepted=None
        for strategy in ['baseline','inside','outside']:
            variant=project/strategy
            (variant/'spec/js').mkdir(parents=True);(variant/'config').mkdir()
            (variant/'config/provengo.yml').write_text('version: 2\n')
            (variant/'spec/js/probe.js').write_text(model_source(args.base_url,strategy),encoding='utf-8')
            samples=variant/'samples.json'
            response=native(['sample','--algorithm','random','--size','1','--max-length','8','-o',str(samples)],variant)
            output=response.stdout+'\n'+response.stderr
            (variant/'sample-output.txt').write_text(redact(output),encoding='utf-8')
            item={'strategy':strategy,'sample_exit_code':response.returncode,'sample_exists':samples.exists()}
            status['variants'].append(item)
            try:
                if response.returncode or not samples.exists():
                    raise ValueError('Native sampling did not produce a sample; inspect this variant sample-output.txt, including SCOPE_STAGE markers.')
                item['sample_bytes']=samples.stat().st_size
                item['serialized_callback_bytes']=inspect_sample(samples,strategy!='baseline')
                item['sampling_accepted']=True
                if strategy!='baseline' and accepted is None:accepted=(variant,samples)
            except Exception as error:
                item['sampling_accepted']=False;item['error']=redact(str(error))
            if strategy=='baseline' and not item['sampling_accepted']:
                raise ValueError('Ordinary callback baseline failed. Scope isolation is not yet implicated.')
        if accepted is None:
            raise ValueError('Neither isolated variant passed. No native HTTP replay was started.')
        variant,samples=accepted
        response=native(['--batch-mode','run','--run-source',str(samples),'--run-id','1','--output-file',str(variant/'native-result.json')],variant)
        output=response.stdout+'\n'+response.stderr
        (variant/'run-output.txt').write_text(redact(output),encoding='utf-8')
        status['run_exit_code']=response.returncode
        result=variant/'native-result.json'
        result_text=result.read_text(encoding='utf-8-sig') if result.exists() else ''
        if response.returncode or 'SBT_SCOPE_PROBE_NATIVE_PASS' not in output+result_text:
            raise ValueError('Native callback execution or RTV continuity was not accepted.')
        status['status']='SCOPE_PROBE_NATIVE_PASS';code=0
    except Exception as error:
        status['error']=redact(str(error))
    finally:
        write(project/'probe-acceptance.json',status)
        review=Path(args.review_zip);review.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(review,'w',zipfile.ZIP_DEFLATED) as archive:
            for path in project.rglob('*'):
                if path.is_file() and path.name != 'samples.json' and path.stat().st_size <= 4*1024*1024:
                    archive.write(path,path.relative_to(project))
        print(json.dumps(status,indent=2));print('Review ZIP:',review);print('Existing models and samples were not modified.')
    return code

if __name__=='__main__':raise SystemExit(main())
