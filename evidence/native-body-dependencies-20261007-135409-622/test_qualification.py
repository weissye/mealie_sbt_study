import copy,json,unittest
from qualification import qualify

def synthetic(mode):
 states={};receipts=[]
 def add(method,path,status,body=None):receipts.append({'method':method,'path':path,'status':status,'states':copy.deepcopy(states),'request_body':copy.deepcopy(body)})
 for name in ['units','resources','foods']:
  path='/'+name+'/'+name+'-1';states[path]={'id':name+'-1','name':'initial'}
  add('POST','/'+name,201);add('GET',path,200);add('GET',path,200);states[path]['name']='updated';add('PATCH',path,200);add('GET',path,200)
 body={'food':copy.deepcopy(states['/foods/foods-1']),'unit':copy.deepcopy(states['/units/units-1']),'amount':1}
 if mode=='changed':states['/units/units-1']['name']='injected-change'
 status=200 if mode=='control' else 500;add('POST','/resources/resources-1/action',status,body);reads=[]
 for logical,path in [('FixtureResource_1','/resources/resources-1'),('Food_1','/foods/foods-1'),('Unit_1','/units/units-1')]:
  add('GET',path,200);reads.append({'logicalId':logical,'code':200,'usable':True,'identityMatches':True,'expectedMatches':not(mode=='changed' and logical=='Unit_1'),'actual':copy.deepcopy(states[path])})
 evidence={'code':status,'captureComplete':True,'observationsComplete':True,'contractStatusValid':mode=='control','readbacks':reads}
 log='OBSERVATION_EVIDENCE '+json.dumps(evidence)+'\n'
 log+='Test Result: SUCCESS' if mode=='control' else 'FAIL: Observation incomplete or contract failure after readbacks\nTest Result: FAIL'
 return 0 if mode=='control' else 1,log,receipts

class Qualification(unittest.TestCase):
 def test_three_synthetic_cases(self):
  for mode in ['control','error','changed']:
   self.assertTrue(qualify(mode,*synthetic(mode))[0])
 def test_missing_dependency_readback(self):
  code,log,r=synthetic('error');r.pop();self.assertFalse(qualify('error',code,log,r)[0])
 def test_wrong_wire_identity(self):
  code,log,r=synthetic('control');r[15]['request_body']['food']['id']='fabricated';self.assertFalse(qualify('control',code,log,r)[0])
 def test_native_error_not_accepted(self):
  _,log,r=synthetic('error');self.assertFalse(qualify('error',2,log.replace('Test Result: FAIL','Test Result: ERROR'),r)[0])
 def test_wrong_readback_identity(self):
  code,log,r=synthetic('error');self.assertFalse(qualify('error',code,log.replace('"identityMatches": true','"identityMatches": false'),r)[0])
 def test_failed_lifecycle_not_accepted(self):
  code,log,r=synthetic('control');r[0]['status']=500;self.assertFalse(qualify('control',code,log,r)[0])

if __name__=='__main__':unittest.main()
