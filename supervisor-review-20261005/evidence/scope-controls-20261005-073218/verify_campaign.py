"""Independent frozen verification; no server requests or file mutations."""
import ast,hashlib,io,json
from pathlib import Path
import zipfile
from qualification_oracle import IdentityMismatch,validate_identity_receipts

def require(condition,message):
 if not condition:raise ValueError(message)

def verify(root):
 checksum=json.loads((root/'checksums.json').read_text(encoding='utf-8-sig'))
 for name,entry in checksum.items():
  require(Path(name).name==name,'Invalid checksum path')
  b=(root/name).read_bytes()
  if entry['normalized_lf']:b=b.replace(b'\r\n',b'\n')
  require(hashlib.sha256(b).hexdigest()==entry['sha256'],'Checksum mismatch: '+name)
 results=[];namespaces=set()
 with zipfile.ZipFile(root/'campaign-original.zip') as campaign:
  require(campaign.testzip() is None,'Campaign CRC failure')
  runs=json.loads(campaign.read('campaign-summary.json'))['runs']
  require({(r['case'],r['sample']) for r in runs}=={(c,n) for c in ('reference-controls','household-controls') for n in (1,2)} and len(runs)==4,'Unexpected cases')
  for run in runs:
   payload=campaign.read(f"{run['case']}/live-{run['sample']}.zip")
   require(hashlib.sha256(payload).hexdigest()==run['sha256'],'Nested archive SHA mismatch')
   with zipfile.ZipFile(io.BytesIO(payload)) as live:
    require(live.testzip() is None,'Live CRC failure')
    acceptance=json.loads(live.read('run-acceptance.json'));receipt=acceptance['runtime_receipt'];plan=json.loads(live.read('relationship_scenario_plan.json'))
    require(acceptance['native_exit']==0 and receipt['status']=='LIVE_CALLBACKS_COMPLETE','Incomplete run')
    evidence=receipt['identity_program'];o=evidence['observations'];order=evidence['order'];namespace=evidence['namespace']
    require(namespace not in namespaces,'Repeated namespace');namespaces.add(namespace)
    require(len(o)==(47 if run['case']=='reference-controls' else 46),'Wrong response count')
    try:validate_identity_receipts(receipt,plan);raise ValueError('Expected discrepancies absent')
    except IdentityMismatch as exc:issues=ast.literal_eval(str(exc))
    keys={(i.get('step',i.get('check')),i['kind']) for i in issues}
    expected={(prefix+a,'HTTP_POLICY_MISMATCH') for a in ('a','b') for prefix in ('cross_add_','missing_add_')} if run['case']=='reference-controls' else {(f'other_list_add_{a}','HTTP_POLICY_MISMATCH') for a in ('a','b')}|{(f'other-list-no-effect-{a}-listItems','STATE_POLICY_MISMATCH') for a in ('a','b')}
    require(keys==expected and len(issues)==4,'Unexpected policy issues')
    require(all(i['observed']==500 for i in issues if i['kind']=='HTTP_POLICY_MISMATCH'),'Unexpected HTTP status')
    for actor in ('a','b'):
     user=o['self_'+actor]['body']
     require(all(user[k] is False for k in ('admin','canManage','canManageHousehold','canOrganize','canInvite')),'Elevated actor')
     require(o['add_'+actor]['code']==200,'Own-list positive control failed')
    changes=[]
    if run['case']=='reference-controls':
     require(all(o['missing_read_'+a]['code']==404 for a in ('a','b')),'Absence control failed')
    else:
     require(o['self_a']['body']['groupId']==o['self_b']['body']['groupId'],'Different groups')
     require(o['self_a']['body']['householdId']!=o['self_b']['body']['householdId'],'Same household')
     steps={s['id']:s for s in plan['identity_program']['steps']}
     for actor,other in [('a','b'),('b','a')]:
      before=o['cross_list_'+other]['body'];after=o['owner_list_after_'+actor]['body']
      require(o['cross_read_'+actor]['code']==200 and o['cross_add_'+actor]['code']==200,'Permitted sharing control failed')
      require(o['other_list_read_'+actor]['code']==404 and o['other_list_add_'+actor]['code']==500,'Unexpected foreign-list results')
      require(o['owner_list_after_'+actor]['code']==200,'Owner readback failed')
      require(before['id']==after['id']==o['list_'+other]['body']['id'],'Wrong victim list')
      require(after['householdId']==o['self_'+other]['body']['householdId'] and after['householdId']!=o['self_'+actor]['body']['householdId'],'Wrong ownership boundary')
      old={i['id']:i for i in before['listItems']};new={i['id']:i for i in after['listItems']};added=set(new)-set(old)
      require(len(old)==2 and len(new)==3 and len(added)==1 and set(old)<=set(new),'Unexpected item delta')
      require(all(new[k]==v for k,v in old.items()),'Existing items also changed')
      item=new[next(iter(added))]
      require(item['quantity']==2 and item['householdId']==after['householdId'],'Unexpected added item')
      require([r['recipeId'] for r in item['recipeReferences']]==[o['before_'+actor]['body']['id']],'Unexpected recipe reference')
      require(before['recipeReferences']==after['recipeReferences'],'Root references also changed')
      targeted=[]
      for sid in order[order.index('cross_list_'+other)+1:order.index('owner_list_after_'+actor)]:
       s=steps[sid]
       if s['operation'].split()[0] not in ('POST','PUT','PATCH','DELETE'):continue
       route=s.get('route',{}).get('item_id')
       if isinstance(route,dict) and '$response' in route:
        source,path=route['$response'];value=o[source]['body'][path]
        if value==after['id']:targeted.append(sid)
      require(targeted==['other_list_add_'+actor],'Intervening mutation of victim list')
      changes.append({'actor':actor.upper(),'victim':other.upper(),'list_id':after['id'],'new_item_id':item['id'],'quantity':item['quantity'],'recipe_id':o['before_'+actor]['body']['id'],'before_items':2,'after_items':3})
    results.append({'case':run['case'],'sample':run['sample'],'sha256':run['sha256'],'responses':len(o),'http_500_count':sum(i['kind']=='HTTP_POLICY_MISMATCH' for i in issues),'unauthorized_changes':changes})
  require(json.loads(campaign.read('server-logs-status.json'))['status']=='CAPTURED','Server logs absent')
  logs=campaign.read('server-logs.txt').decode('utf-8')
  require('mealie.core.exceptions.UnexpectedNone: Recipe not found' in logs,'Missing-reference exception absent')
  require("AttributeError: 'NoneType' object has no attribute 'list_items'" in logs,'Foreign-list exception absent')
 return results

if __name__=='__main__':
 results=verify(Path(__file__).resolve().parent)
 print('SCOPE_FINDINGS_VERIFIED: 186 responses; existing missing-reference error; four reproduced cross-household list mutations after HTTP 500. No API requests sent.')
