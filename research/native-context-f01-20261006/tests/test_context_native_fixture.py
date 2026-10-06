import json,subprocess,threading,shutil,uuid,re,os
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import argparse,sys
parser=argparse.ArgumentParser()
parser.add_argument('--jar',required=True)
parser.add_argument('--output',required=True)
parser.add_argument('--missing-link',action='store_true')
args=parser.parse_args()
source_root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(source_root))
from generator_v56.render.context_model import generate_context_model
root=Path(args.output).resolve()
if root.exists():raise SystemExit('Use a new output directory')
state={};requests=[]
class H(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def handle_request(self):
  data=self.rfile.read(int(self.headers.get('Content-Length',0)))
  path=self.path
  requests.append({'method':self.command,'path':path})
  if path=='/api/auth/token':return self.reply(200,{'access_token':'dummy-token','token_type':'bearer'})
  body=json.loads(data) if data else None
  if self.command=='POST':
   id=str(uuid.uuid4());obj=dict(body or {});obj['id']=id
   obj.update(userId='fixture-user',groupId='fixture-group',householdId='fixture-household')
   if path=='/api/recipes':
    obj['slug']=obj['name'].lower();detail=path+'/'+obj['slug'];state[detail]=obj
    return self.reply(201,obj['slug'])
   state[path+'/'+id]=obj
   if path.endswith('/items'):return self.reply(201,{'createdItems':[obj],'updatedItems':[],'deletedItems':[]})
   return self.reply(201,obj)
  if path not in state:return self.reply(404,{'detail':'not found'})
  if self.command in ('PUT','PATCH'):state[path].update(body)
  observed=dict(state[path])
  if args.missing_link and self.command=='GET' and '/shopping/items/' in path:observed['recipeReferences']=[]
  self.reply(200,observed)
 def do_GET(self):self.handle_request()
 def do_POST(self):self.handle_request()
 def do_PUT(self):self.handle_request()
 def do_PATCH(self):self.handle_request()
 def reply(self,code,data):
  b=json.dumps(data).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
s=ThreadingHTTPServer(('127.0.0.1',0),H);threading.Thread(target=s.serve_forever,daemon=True).start()
generate_context_model(source_root/'model/mealie-openapi.v3.28.0.json',root/'spec/js','mealie','http://127.0.0.1:'+str(s.server_port),['/api/foods','/api/units','/api/recipes','/api/households/shopping/lists','/api/households/shopping/items'],1,920571960)
env=dict(os.environ,SBT_USERNAME='fixture',SBT_PASSWORD='fixture')
r=subprocess.run(['java','-jar',str(Path(args.jar).resolve()),'run',str(root)],env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=90)
(root/'fixture-native.log').write_text(r.stdout)
print('EXIT',r.returncode,'HTTP',len(requests))
print(json.dumps(requests))
for l in r.stdout.splitlines():
 if any(t in l for t in ['ERR ','WARN','Test Result']):print(l)
s.shutdown()
(root/'fixture-requests.json').write_text(json.dumps(requests,indent=2))
expected_exit=1 if args.missing_link else 0
report={'status':'NATIVE_FIXTURE_EXPECTED_RESULT' if r.returncode==expected_exit else 'NATIVE_FIXTURE_UNEXPECTED_RESULT','exit_code':r.returncode,'expected_exit':expected_exit,'http_requests':len(requests),'native_provengo_executed':True,'mealie_requests':0,'missing_link_injected':args.missing_link}
(root/'fixture-result.json').write_text(json.dumps(report,indent=2))
if r.returncode!=expected_exit:raise SystemExit(1)

