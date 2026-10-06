"""Actual native Provengo against a deterministic HTTP fixture, not the Mealie SUT."""
import argparse,json,os,subprocess,sys,threading,uuid
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
parser=argparse.ArgumentParser();parser.add_argument('--jar',required=True);parser.add_argument('--output',required=True);parser.add_argument('--fault',choices=['quantity','reference','identity','duplicate']);args=parser.parse_args()
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from generator_v56.render.context_model import generate_context_model
out=Path(args.output);state={};requests=[];stage=0
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def reply(self,code,data):
  b=json.dumps(data).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def handle_request(self):
  global stage
  raw=self.rfile.read(int(self.headers.get('Content-Length',0)));path=self.path
  requests.append({'method':self.command,'path':path})
  if path=='/api/auth/token':return self.reply(200,{'access_token':'dummy-token','token_type':'bearer'})
  body=json.loads(raw) if raw else None
  if self.command=='POST' and path.endswith('/recipe'):
   stage+=1;lst=state[path[:-7]];param=body[0];recipe=next(o for k,o in state.items() if k.startswith('/api/recipes/') and o['id']==param['recipeId'])
   scale=param['recipeIncrementQuantity'];quantity=sum(x['quantity'] for x in recipe['recipeIngredient'])*scale
   if not lst.get('listItems'):
    first=recipe['recipeIngredient'][0];id=str(uuid.uuid4());item={'id':id,'quantity':0,'shoppingListId':lst['id'],'foodId':first['food']['id'],'unitId':first['unit']['id'],'recipeReferences':[{'id':str(uuid.uuid4()),'recipeId':recipe['id'],'recipeQuantity':sum(x['quantity'] for x in recipe['recipeIngredient']),'recipeScale':0,'shoppingListItemId':id}]};lst['listItems']=[item];state['/api/households/shopping/items/'+id]=item
    lst['recipeReferences']=[{'id':str(uuid.uuid4()),'shoppingListId':lst['id'],'recipeId':recipe['id'],'recipeQuantity':0}]
   item=lst['listItems'][0];item['quantity']+=quantity;item['recipeReferences'][0]['recipeScale']+=scale;lst['recipeReferences'][0]['recipeQuantity']+=scale
   if stage==2:
    if args.fault=='quantity':item['quantity']+=1
    if args.fault=='reference':item['recipeReferences'][0]['recipeQuantity']+=1
    if args.fault=='identity':item['id']=str(uuid.uuid4())
    if args.fault=='duplicate':lst['listItems'].append(dict(item,id=str(uuid.uuid4())))
   return self.reply(200,lst)
  if self.command=='POST':
   id=str(uuid.uuid4());obj=dict(body or {},id=id,userId='fixture',groupId='fixture',householdId='fixture')
   if path=='/api/recipes':obj['slug']=obj['name'].lower();state[path+'/'+obj['slug']]=obj;return self.reply(201,obj['slug'])
   if path.endswith('/lists'):obj.update(listItems=[],recipeReferences=[])
   state[path+'/'+id]=obj
   return self.reply(201,obj)
  if path not in state:return self.reply(404,{'detail':'absent'})
  if self.command in ('PATCH','PUT'):state[path].update(body)
  self.reply(200,state[path])
 def do_GET(self):self.handle_request()
 def do_POST(self):self.handle_request()
 def do_PATCH(self):self.handle_request()
 def do_PUT(self):self.handle_request()
server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
generate_context_model(root/'model/mealie-openapi.v3.28.0.json',out/'spec/js','mealie','http://127.0.0.1:'+str(server.server_port),['/api/foods','/api/units','/api/recipes','/api/households/shopping/lists','/api/households/shopping/items'],1,20261006,True)
try:
 result=subprocess.run(['java','-jar',str(Path(args.jar).resolve()),'run',str(out)],env=dict(os.environ,SBT_USERNAME='fixture',SBT_PASSWORD='fixture'),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=90)
finally:server.shutdown()
(out/'native-fixture.log').write_text(result.stdout)
expected=1 if args.fault else 0
post=[i for i,r in enumerate(requests) if r['method']=='POST' and r['path'].endswith('/recipe')]
assert len(post)==2,(post,result.stdout[-2000:])
assert all(r['method']=='GET' for r in requests[post[-1]+1:])
assert len(requests[post[-1]+1:])==4,'Independent readbacks missing'
assert result.returncode==expected,result.stdout[-4000:]
assert ('Test Result: SUCCESS' in result.stdout)==(not args.fault)
assert 'F01_EVIDENCE ' in result.stdout
report=dict(status='NATIVE_FIXTURE_REGRESSION_PASS',native_exit=result.returncode,fault=args.fault,http_requests=len(requests),contributions=stage,independent_readbacks_after_second=4,native_provengo_executed=True,mealie_executed=False)
(out/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
