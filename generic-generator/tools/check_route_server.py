"""Read pinned server metadata through a generated Provengo interface; no mutations."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.audit_route_state import FACTORY
from tools.relationship_execution import native,redact


def check(root,base_url,review):
    origin=urlsplit(base_url)
    if origin.scheme not in ('http','https') or not origin.netloc or origin.username or origin.password or origin.query or origin.fragment or origin.path not in ('','/'):
        raise ValueError('Expected an HTTP origin without credentials or a path.')
    expected=json.loads((root/'generic-generator/compatibility/contracts/mealie.json').read_text(encoding='utf-8-sig'))['info']['version']
    project=root/'provengo'/('route-server-check-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f'))
    (project/'spec/js').mkdir(parents=True);(project/'config').mkdir();review.mkdir(parents=True,exist_ok=True)
    (project/'config/provengo.yml').write_text('version: 2\n',encoding='utf-8')
    callback="var body=JSON.parse(response.body);pvg.rtv.set('route_server_contract',JSON.stringify({code:response.code,version:body.info.version}));"
    interfaces='//@provengo summon rest\nconst checkSvc=new RESTSession('+json.dumps(base_url.rstrip('/'))+',"route-server-check");\n'+FACTORY+'\nfunction checkContract(){checkSvc.get("/openapi.json",{expectedResponseCodes:[200],callback:auditCallback('+json.dumps(callback)+')});}\n'
    (project/'spec/js/interfaces.server-check.js').write_text(interfaces,encoding='utf-8')
    (project/'spec/js/stories.server-check.js').write_text("bthread('check-server-contract',function(){checkContract();});\n",encoding='utf-8')
    sampled=native(['sample','--size','1','--max-length','4','-o','samples.json'],project)
    (review/'server-check-sample-output.txt').write_text(redact(sampled.stdout+sampled.stderr),encoding='utf-8')
    if sampled.returncode!=0 or not (project/'samples.json').is_file():raise ValueError('Server metadata sampling failed.')
    samples=json.loads((project/'samples.json').read_text());events=[e['data'] for sample in samples for e in sample if (e.get('data') or {}).get('lib')=='REST']
    if len(samples)!=1 or len(events)!=1 or events[0].get('method')!='GET' or events[0].get('url')!=base_url.rstrip('/')+'/openapi.json':raise ValueError('Invalid read-only preflight sample.')
    run=native(['--batch-mode','run','--run-source','samples.json','--run-id','1'],project)
    output=redact(run.stdout+run.stderr);(review/'server-check-run-output.txt').write_text(output,encoding='utf-8')
    observations=[]
    for m in re.finditer(r"setting 'route_server_contract' to '(\{)",output):
        try:observations.append(json.JSONDecoder().raw_decode(output[m.start(1):])[0])
        except ValueError:continue
    status={'status':'SERVER_METADATA_NOT_ACCEPTED','expected_version':expected,'resource_mutations':0,'project':str(project)}
    if run.returncode==0 and len(observations)==1:
        status['observed']=observations[0]
        if observations[0]==dict(code=200,version=expected):status['status']='PINNED_SERVER_VERSION_PASS'
    (review/'server-check.json').write_text(json.dumps(status,indent=2)+'\n',encoding='utf-8')
    if status['status']!='PINNED_SERVER_VERSION_PASS':raise ValueError('Server unavailable or pinned version mismatch. Inspect server-check evidence.')
    return status


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--base-url',required=True);p.add_argument('--review',required=True);a=p.parse_args()
    try:print(json.dumps(check(Path(a.root),a.base_url,Path(a.review)),indent=2))
    except Exception as error:print('SERVER_CHECK_NOT_ACCEPTED: '+str(error));raise SystemExit(1)
