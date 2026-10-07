import json,copy
from http.server import BaseHTTPRequestHandler

class Fixture(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def body(self):return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
 def reply(self,status,body,request=None):
  payload=body.encode() if isinstance(body,str) else json.dumps(body).encode()
  self.server.receipts.append({'method':self.command,'path':self.path,'status':status,'request_body':copy.deepcopy(request),'states':copy.deepcopy(self.server.states)})
  self.send_response(status);self.send_header('Content-Type','text/plain' if isinstance(body,str) else 'application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
 def do_POST(self):
  body=self.body()
  if self.path in ['/resources','/foods','/units']:
   identifier=self.path[1:]+'-1';state={'id':identifier,'name':body['name']};self.server.states[self.path+'/'+identifier]=state;self.reply(201,state,body)
  elif self.path=='/resources/resources-1/action':
   expected_food=self.server.states.get('/foods/foods-1');expected_unit=self.server.states.get('/units/units-1')
   if body.get('food')!=expected_food or body.get('unit')!=expected_unit or body.get('amount')!=1:
    self.reply(422,{'detail':'Body identity/projection mismatch'},body);return
   if self.server.mode=='changed':self.server.states['/units/units-1']['name']='injected-change'
   self.reply(200 if self.server.mode=='control' else 500,self.server.states['/resources/resources-1'] if self.server.mode=='control' else 'Internal Server Error',body)
  else:self.reply(404,{},body)
 def do_PATCH(self):
  body=self.body()
  if self.path in self.server.states:self.server.states[self.path].update(body);self.reply(200,self.server.states[self.path],body)
  else:self.reply(404,{},body)
 def do_GET(self):self.reply(200,self.server.states[self.path]) if self.path in self.server.states else self.reply(404,{})
