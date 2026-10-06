"""HTTP callback regression tests; not a native Provengo engine substitute."""
import copy, importlib.util, json, shutil, subprocess, tempfile, threading, unittest
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from compile_native_lifecycle import bind,render
ROOT=Path(__file__).resolve().parents[1]
PROFILE=json.loads((ROOT/'profiles/mealie-native-f01.json').read_text())


def fixture_contract():
    # Synthetic schema, deliberately identified as fixture, never shipped as pinned OpenAPI.
    obj=lambda fields:{'type':'object','properties':{k:({'type':'number'} if k in ('quantity','recipeIncrementQuantity') else {'type':'string'}) for k in fields}}
    doc={'openapi':'3.0.3','info':{'title':'SYNTHETIC CONTRACT FIXTURE','version':'test'},'paths':{}}
    schemas={
      'food_create':obj(['name']),'unit_create':obj(['name']),'list_create':obj(['name']),
      'recipe_create':obj(['name']),
      'recipe_update':{'type':'object','properties':{'id':{'type':'string'},'name':{'type':'string'},'settings':{'type':'object'},'recipeIngredient':{'type':'array','items':{'type':'object','properties':{'quantity':{'type':'number'},'food':obj(['id','name']),'unit':obj(['id','name']),'note':{'type':'string'}}}}}},
      'item_create':obj(['shoppingListId','foodId','unitId','quantity','note']),
      'contribution':obj(['recipeIncrementQuantity'])}
    for key,op in PROFILE['operations'].items():
        entry={'operationId':key,'responses':{'201' if op['method']=='POST' else '200':{'description':'ok'}}}
        if key in schemas:entry['requestBody']={'content':{'application/json':{'schema':schemas[key]}}}
        doc['paths'].setdefault(op['path'],{})[op['method'].lower()]=entry
    return doc

class Fixture(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def handle_request(self):
        state=self.server.state;length=int(self.headers.get('Content-Length',0));raw=self.rfile.read(length);body=json.loads(raw) if raw and 'application/json' in self.headers.get('Content-Type','') else {}
        method=self.command;path=self.path;code=201 if method=='POST' else 200
        if path=='/api/auth/token':out={'access_token':'fixture-token'};code=200
        elif path in ['/api/foods','/api/units','/api/recipes','/api/households/shopping/lists']:
            key={'/api/foods':'food','/api/units':'unit','/api/recipes':'recipe','/api/households/shopping/lists':'list'}[path]
            out=dict(body,id=key+'-id')
            if key=='recipe':out.update(slug='fixture-recipe',settings={'disableAmounts':True},recipeIngredient=[])
            if key=='list':out.update(listItems=[],recipeReferences=[])
            state[key]=out
            if key=='recipe':out='fixture-recipe'
        elif path=='/api/households/shopping/items':
            item=dict(body,id='item-id',food=state['food'],unit=state['unit']);state['list']['listItems']=[item];out={'createdItems':[item],'updatedItems':[],'deletedItems':[]}
        elif '/recipe/recipe-id' in path:
            scale=body['recipeIncrementQuantity'];delta=4*scale
            if self.server.fault=='fraction' and scale==0.5:delta=3
            state['list']['listItems'][0]['quantity']+=delta
            refs=state['list']['recipeReferences']
            if not refs:refs.append({'recipeId':'recipe-id','recipeQuantity':0})
            refs[0]['recipeQuantity']+=scale
            if self.server.fault=='association' and scale==0.5:refs[0]['recipeQuantity']+=1
            out=state['list']
        else:
            key='food' if '/foods/' in path else 'unit' if '/units/' in path else 'recipe' if '/recipes/' in path else 'list'
            if method=='PUT':state[key]=body
            out=state[key]
        payload=json.dumps(out).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
    do_GET=do_POST=do_PUT=handle_request

NODE_HARNESS=r'''
const vm=require('vm'),fs=require('fs'),cp=require('child_process');const variables={},messages=[];
global.pvg={rtv:{get:k=>variables[k],set:(k,v)=>variables[k]=v},success:x=>{},fail:x=>{throw Error(x)}};
global.bp={log:{info:x=>messages.push(x)}};
function expand(s){return s.replace(/@\{([^}]+)\}/g,(_,k)=>k.startsWith("getEnv(")?'fixture':variables[k]);}
global.RESTSession=function(base,name){for(const method of ['get','post','put'])this[method]=(path,args)=>{
 let req={url:base+expand(path),method:method.toUpperCase(),headers:Object.fromEntries(Object.entries(args.headers).map(([k,v])=>[k,expand(v)])),body:args.body===undefined?null:expand(args.body)};
 let raw=cp.execFileSync(process.env.TEST_PYTHON,['-c',`import json,sys,urllib.request
r=json.load(sys.stdin);b=r['body'];q=urllib.request.Request(r['url'],data=b.encode() if b is not None else None,headers=r['headers'],method=r['method'])
with urllib.request.urlopen(q) as x:print(json.dumps({'status':x.status,'body':x.read().decode()}))`],{input:JSON.stringify(req),encoding:'utf8'});
 let response=JSON.parse(raw);if(!args.expectedResponseCodes.includes(response.status))throw Error('Unexpected fixture status');args.callback(response);
};};
vm.runInThisContext(fs.readFileSync(process.argv[2],'utf8'));
try{nativeLogin();for(const key of JSON.parse(process.argv[3])){nativeStep(key);nativeVerify(key);}console.log('CALLBACK_FIXTURE_PASS');}
catch(e){console.log(e.message);console.log(messages.filter(x=>x.startsWith('NATIVE_QUANTITY_OBSERVATION')).join('\n'));process.exitCode=2;}
'''

class Tests(unittest.TestCase):
    def test_missing_operation_stops_generation(self):
        doc=fixture_contract();del doc['paths']['/api/recipes']
        with self.assertRaises(ValueError):bind(doc,PROFILE)
    def test_increment_field_is_contract_bound(self):
        doc=fixture_contract();b=bind(doc,PROFILE);self.assertEqual(b['operations']['contribution']['increment_field'],'recipeIncrementQuantity')
        entry=doc['paths'][PROFILE['operations']['contribution']['path']]['post'];entry['requestBody']['content']['application/json']['schema']['properties']={'other':{'type':'number'}}
        with self.assertRaises(ValueError):bind(doc,PROFILE)
    def test_stories_have_entities_dependencies_and_action_verifiers(self):
        i,s,b=render(fixture_contract(),PROFILE,'http://127.0.0.1:1','test')
        self.assertEqual(s.count('bthread("lifecycle:'),5);self.assertEqual(s.count('bthread("verify:'),8)
        self.assertIn('"food", "unit"',s);self.assertNotIn('RESTSession',s);self.assertNotIn('svc.',s);self.assertNotIn('Coordinator',s)
        self.assertEqual(b['steps']['half-recipe']['body'],{'recipeIncrementQuantity':0.5})
    @unittest.skipUnless(shutil.which('node'),'Node not installed')
    def test_http_success_and_injected_arithmetic_and_association_faults(self):
        import os,sys
        for fault,expected in [('',0),('fraction',2),('association',2)]:
            for prefix in [['food-create','unit-create','list-create'],['list-create','unit-create','food-create']]:
                with self.subTest(fault=fault,prefix=prefix):
                    server=ThreadingHTTPServer(('127.0.0.1',0),Fixture);server.state={};server.fault=fault
                    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
                    try:
                        with tempfile.TemporaryDirectory() as d:
                            p=Path(d);interfaces,_,_=render(fixture_contract(),PROFILE,'http://127.0.0.1:'+str(server.server_port),'fixture')
                            (p/'interfaces.js').write_text(interfaces);(p/'harness.js').write_text(NODE_HARNESS)
                            order=prefix+['recipe-create','recipe-build','manual-baseline','whole-recipe','half-recipe']
                            r=subprocess.run(['node',str(p/'harness.js'),str(p/'interfaces.js'),json.dumps(order)],capture_output=True,text=True,env=dict(os.environ,TEST_PYTHON=sys.executable))
                            self.assertEqual(r.returncode,expected,r.stdout+r.stderr)
                            if fault:self.assertIn('F01_QUANTITY_CANDIDATE',r.stdout)
                    finally:server.shutdown();server.server_close()
if __name__=='__main__':unittest.main()
