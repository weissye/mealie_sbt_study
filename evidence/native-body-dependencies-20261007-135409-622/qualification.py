import json

def qualify(mode,code,log,receipts):
 reasons=[];marker='OBSERVATION_EVIDENCE '
 try:evidence=[json.loads(s.split(marker,1)[1]) for s in log.splitlines() if marker in s]
 except (ValueError,IndexError):return False,['Malformed evidence marker']
 actions=[(i,r) for i,r in enumerate(receipts) if r['path']=='/resources/resources-1/action']
 if len(actions)!=1 or len(evidence)!=1:return False,['Missing/repeated action or evidence']
 index,action=actions[0]
 if index!=15 or len(receipts)!=19:reasons.append('Lifecycle/readback request counts differ')
 targets={'FixtureResource_1':'/resources/resources-1','Food_1':'/foods/foods-1','Unit_1':'/units/units-1'}
 for path in targets.values():
  collection=path.rsplit('/',1)[0]
  actual=[(r['method'],r['path'],r['status']) for r in receipts[:index] if r['path'] in [path,collection]]
  expected=[('POST',collection,201),('GET',path,200),('GET',path,200),('PATCH',path,200),('GET',path,200)]
  if actual!=expected:reasons.append('Incomplete lifecycle: '+path)
 baseline=receipts[index-1]['states'] if index else {}
 body=action.get('request_body',{})
 if body!={'food':baseline.get('/foods/foods-1'),'unit':baseline.get('/units/units-1'),'amount':1}:reasons.append('Wire body lacks real verified dependency identities/projections')
 status=200 if mode=='control' else 500
 if action['status']!=status:reasons.append('Action status differs')
 after=receipts[index+1:]
 if [(r['method'],r['path'],r['status']) for r in after]!=[('GET',p,200) for p in targets.values()]:reasons.append('Three ordered independent readbacks not completed')
 e=evidence[0];reads=e.get('readbacks',[])
 if e.get('code')!=status or not e.get('captureComplete') or not e.get('observationsComplete'):reasons.append('Capture/readbacks incomplete')
 if e.get('contractStatusValid')!=(mode=='control'):reasons.append('Wrong contract classification')
 if len(reads)!=3:reasons.append('Wrong number of callback readbacks')
 else:
  for read,(logical,path),receipt in zip(reads,targets.items(),after):
   if read.get('logicalId')!=logical or not read.get('identityMatches') or not read.get('usable') or read.get('code')!=200:reasons.append('Unusable identity readback: '+logical)
   if read.get('actual')!=receipt['states'].get(path):reasons.append('Callback does not match independent fixture read: '+logical)
   if read.get('expectedMatches')!=(mode!='changed' or logical!='Unit_1'):reasons.append('Wrong DAL comparison: '+logical)
 final=receipts[-1]['states'];expected={k:dict(v) for k,v in baseline.items()}
 if mode=='changed':expected['/units/units-1']['name']='injected-change'
 if final!=expected:reasons.append('Unexpected final fixture state')
 if mode=='control':
  if code!=0 or not any('Test Result: '+s in log for s in ['SUCCESS','PASS']):reasons.append('Native control did not succeed')
 else:
  failure='FAIL: Observation incomplete or contract failure after readbacks'
  if code!=1 or 'Test Result: FAIL' not in log or failure not in log:reasons.append('Intentional deferred failure missing')
  elif log.index(marker)>log.index(failure):reasons.append('Failure preceded collected evidence')
 return not reasons,reasons
