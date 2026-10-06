"""Offline renderer checks and optional real-native execution against a local fixture."""
import argparse,json,subprocess,sys,threading,unittest,uuid
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer

class NativeFixture:
    def __init__(self,fault=False):
        self.records={};self.requests=[];self.fault=fault
        outer=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def send(self,code,data):
                body=json.dumps(data).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
            def view(self,record):
                record=dict(record)
                if 'name' in record:record['listItems']=[dict(x) for x in outer.records.values() if x.get('shoppingListId')==record['id']]
                return record
            def do_POST(self):
                data=self.rfile.read(int(self.headers.get('Content-Length','0')));outer.requests.append(['POST',self.path])
                if self.path=='/api/auth/token':return self.send(200,{'access_token':'local-fixture-token','token_type':'bearer'})
                body=json.loads(data);key=str(uuid.uuid4())
                if self.path.endswith('/lists'):
                    body.update(id=key,groupId='group-fixture',userId='user-fixture',householdId='household-fixture',listItems=[])
                    outer.records[key]=body;return self.send(201,self.view(body))
                if self.path.endswith('/items'):
                    if body.get('shoppingListId') not in outer.records:return self.send(422,{'detail':'parent unavailable'})
                    body.update(id=key,quantity=1,groupId='group-fixture',householdId='household-fixture');outer.records[key]=body
                    return self.send(201,{'createdItems':[self.view(body)],'updatedItems':[],'deletedItems':[]})
                self.send(404,{})
            def do_GET(self):
                outer.requests.append(['GET',self.path]);key=self.path.rsplit('/',1)[-1]
                self.send(200 if key in outer.records else 404,self.view(outer.records[key]) if key in outer.records else {})
            def do_PUT(self):
                body=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))));outer.requests.append(['PUT',self.path]);key=self.path.rsplit('/',1)[-1]
                if key not in outer.records:return self.send(404,{})
                if not(outer.fault and '/items/' in self.path):outer.records[key].update(body)
                self.send(200,self.view(outer.records[key]))
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=self.server.serve_forever,daemon=True).start()
    def close(self):self.server.shutdown();self.server.server_close()

def execute(root,jar,fault):
    fixture=NativeFixture(fault)
    try:
        command=[sys.executable,'-B',str(Path(__file__).with_name('run_mealie_dependency_acceptance.py')),'--root',str(root.resolve()),'--jar',str(jar.resolve()),'--base-url','http://127.0.0.1:'+str(fixture.server.server_port)]
        result=subprocess.run(command,input='local-fixture-password\n',capture_output=True,text=True,timeout=360)
        print(result.stdout);print(result.stderr)
        expected=2 if fault else 0
        if result.returncode!=expected:raise AssertionError('Native fixture outcome differs: '+str(result.returncode))
        if not fault and len(fixture.requests)!=19:raise AssertionError('Expected 19 HTTP calls')
        return {'status':'INJECTED_NONPERSISTED_UPDATE_DETECTED' if fault else 'LOCAL_NATIVE_DEPENDENCY_FIXTURE_PASS','exit_code':result.returncode,'requests':fixture.requests,'resource_count':len(fixture.records),'target':'Local synthetic fixture only; not Mealie','output':result.stdout}
    finally:fixture.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--jar',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    results=[execute(a.root,a.jar,False),execute(a.root,a.jar,True)];a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(results,indent=2))
