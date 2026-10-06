"""Offline renderer checks and optional real-native execution against a local fixture."""
import argparse,json,subprocess,sys,threading,unittest,uuid
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer

class MergeFixture:
    def __init__(self,fault=False):
        self.records={};self.requests=[];self.fault=fault
        outer=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def send(self,code,data):
                body=json.dumps(data).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
            def view(self,record):
                record=dict(record)
                if 'userId' in record:record['listItems']=[dict(x) for x in outer.records.values() if x.get('shoppingListId')==record['id']]
                if 'shoppingListId' in record:
                    record['food']=dict(outer.records.get(record.get('foodId'),{})) or None
                    record['unit']=dict(outer.records.get(record.get('unitId'),{})) or None
                return record
            def do_POST(self):
                data=self.rfile.read(int(self.headers.get('Content-Length','0')));outer.requests.append(['POST',self.path])
                if self.path=='/api/auth/token':return self.send(200,{'access_token':'local-fixture-token','token_type':'bearer'})
                body=json.loads(data);key=str(uuid.uuid4())
                if self.path in ('/api/foods','/api/units'):
                    body.update(id=key);outer.records[key]=body;return self.send(201,self.view(body))
                if self.path.endswith('/lists'):
                    body.update(id=key,groupId='group-fixture',userId='user-fixture',householdId='household-fixture',listItems=[])
                    outer.records[key]=body;return self.send(201,self.view(body))
                if self.path.endswith('/items'):
                    if body.get('shoppingListId') not in outer.records:return self.send(422,{'detail':'parent unavailable'})
                    if body.get('foodId') not in outer.records or body.get('unitId') not in outer.records:return self.send(422,{'detail':'optional dependency unavailable'})
                    existing=next((x for x in outer.records.values() if all(x.get(k)==body.get(k) for k in ('shoppingListId','foodId','unitId')) and 'shoppingListId' in x),None)
                    if existing:
                        before=dict(existing);existing['quantity']+=body.get('quantity',1);existing['note']+=' | '+body['note']
                        returned=self.view(existing)
                        if outer.fault=='merge-quantity':existing['quantity']+=1;returned=self.view(existing)
                        if outer.fault=='merge-not-persisted':outer.records[existing['id']]=before
                        if outer.fault=='merge-unrelated':
                            other=next(x for x in outer.records.values() if 'shoppingListId' in x and x['id']!=existing['id']);other['quantity']+=1
                        return self.send(201,{'createdItems':[],'updatedItems':[returned],'deletedItems':[]})
                    if outer.fault=='binding':body['unitId']=str(uuid.uuid4())
                    body.update(id=key,quantity=1,groupId='group-fixture',householdId='household-fixture');outer.records[key]=body
                    return self.send(201,{'createdItems':[self.view(body)],'updatedItems':[],'deletedItems':[]})
                self.send(404,{})
            def do_GET(self):
                outer.requests.append(['GET',self.path]);key=self.path.rsplit('/',1)[-1]
                self.send(200 if key in outer.records else 404,self.view(outer.records[key]) if key in outer.records else {})
            def do_DELETE(self):
                outer.requests.append(['DELETE',self.path]);key=self.path.rsplit('/',1)[-1]
                if key not in outer.records:return self.send(404,{})
                parent=outer.records[key].get('shoppingListId')
                if outer.fault!='ignored-delete':del outer.records[key]
                if outer.fault=='deleted-sibling':
                    for sibling in list(outer.records):
                        if outer.records[sibling].get('shoppingListId')==parent:del outer.records[sibling]
                self.send(200,{'message':'deleted'})
            def do_PUT(self):
                body=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))));outer.requests.append(['PUT',self.path]);key=self.path.rsplit('/',1)[-1]
                if key not in outer.records:return self.send(404,{})
                if '/lists/' in self.path and 'listItems' in body:
                    incoming={x['id']:dict(x) for x in body['listItems']}
                    existing=[k for k,x in outer.records.items() if x.get('shoppingListId')==key]
                    for child_id in existing:
                        if child_id not in incoming:del outer.records[child_id]
                    for child_id,x in incoming.items():outer.records[child_id]=x
                    if outer.fault=='parent-drop' and incoming:del outer.records[next(iter(incoming))]
                if outer.fault=='binding-update' and '/items/' in self.path:body['foodId']=str(uuid.uuid4())
                if outer.fault=='scalar' and '/items/' in self.path:
                    body['quantity']=body.get('quantity',1)+1;outer.records[key].update(body)
                elif not(outer.fault is True and '/items/' in self.path):outer.records[key].update(body)
                self.send(200,self.view(outer.records[key]))
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=self.server.serve_forever,daemon=True).start()
    def close(self):self.server.shutdown();self.server.server_close()

def execute(root,jar,scenario,fault=False):
    fixture=MergeFixture(fault)
    try:
        command=[sys.executable,'-B',str(Path(__file__).with_name('run_mealie_distinct_merge.py')),'--root',str(root.resolve()),'--jar',str(jar.resolve()),'--scenario',scenario,'--base-url','http://127.0.0.1:'+str(fixture.server.server_port)]
        result=subprocess.run(command,input='local-fixture-password\n',capture_output=True,text=True,timeout=360)
        print(result.stdout);print(result.stderr)
        if result.returncode!=(2 if fault else 0):raise AssertionError('Unexpected fixture outcome: '+str(result.returncode))
        run=Path(next(line.split('Review ZIP: ',1)[1] for line in result.stdout.splitlines() if line.startswith('Review ZIP: '))).parent
        report=json.loads((run/'acceptance-report.json').read_text())
        if fault and not report.get('native_live_executed'):raise AssertionError('Fault test never reached HTTP')
        if fault:
            log=(run/'live-output.txt').read_text()
            expected={'merge-quantity':'MERGE_RESPONSE_STATE_MISMATCH','merge-not-persisted':'MERGE_PERSISTED_STATE_MISMATCH','merge-unrelated':'Scalar state changed after marker update','binding':'Create optional binding mismatch'}[fault]
            if expected not in log:raise AssertionError('Expected verifier did not detect injected fault: '+expected)
        elif not report['distinct_children_verified']:raise AssertionError('Distinct identity verification missing')
        return {'scenario':scenario,'injected_fault':fault,'exit_code':result.returncode,'http_calls':len(fixture.requests),'review':str(run/'review.zip'),'report':report,'scope':'Local synthetic HTTP fixture; native Provengo JAR; not a Mealie server result'}
    finally:fixture.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--jar',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    results=[execute(a.root,a.jar,'distinct'),execute(a.root,a.jar,'merge')]
    for fault in ('merge-quantity','merge-not-persisted','merge-unrelated'):results.append(execute(a.root,a.jar,'merge',fault))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(results,indent=2))
