import copy,hashlib,io,json,re,sys,zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'generic-generator/tools'))
archive = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent/'campaign.zip'
if hashlib.sha256(archive.read_bytes()).hexdigest() != 'f360a4b7c8a9c4cf14d92a27f5bc9cbe602f99672750a17250a20d2ceb833b34':
 raise SystemExit('Original campaign SHA256 mismatch.')
from semantic_receipts import validate_semantic_receipts
from relationship_execution import find_receipt
out=[]
with zipfile.ZipFile(archive) as outer:
 for n in outer.namelist():
  if not re.search(r'live-[12]\.zip$',n):continue
  case=n.replace('\\','/').split('/')[0]
  with zipfile.ZipFile(io.BytesIO(outer.read(n))) as z:
   plan=json.loads(z.read('relationship_scenario_plan.json'));lines=z.read('execution-review/run-output.txt').decode('utf-8-sig').splitlines();accept=json.loads(z.read('execution-review/run-acceptance.json'))
  vals={}
  for l in lines:
   m=re.search(r"RTV: setting '([^']+)' to '(.*)'$",l)
   if m:
    try:vals[m[1]]=json.loads(m[2])
    except:pass
  rs=vals['sbt_rel_semantic_receipts'];ids={r['task_id'] for r in rs}
  partial=copy.deepcopy(plan);partial['tasks']=[t for t in plan['tasks'] if not t['kind'].startswith('semantic_') or t['id'] in ids]
  validate_semantic_receipts({'semantic_tests':rs,'owned_records':vals['sbt_rel_owned']},partial)
  r={'case':case,'sample':int(n[-5]),'status':accept['status'],'independent_prefix_validation':'PASS','completed_semantic':len(rs),'completed_order':[t['task_id'] for t in rs], 'resource_ids':[x['route'].get('id') for x in vals['sbt_rel_owned']]}
  if accept.get('live_accepted'):
   receipt=find_receipt('\n'.join(lines));validate_semantic_receipts(receipt,plan)
   r.update(native_success=any('Test Result: SUCCESS' in l for l in lines),http_responses=receipt['response_count'],final_manual_totals=[sum(rs[-1]['expected'][i]['totals'].values()) for i in plan['instances']['api/households/shopping/lists']])
  else:
   warning=next(l for l in lines if ' WARN [' in l and 'FAIL: Semantic consistency mismatch:' in l)
   fail=json.loads(warning.split('FAIL: Semantic consistency mismatch: ',1)[1].removesuffix('.'))
   pending=next(v for k,v in vals.items() if k.endswith('_semantic') and isinstance(v,dict) and v.get('task_id') not in ids)
   source=pending['reference_instance'];dest=pending['container'];amount=pending['amount'];before=pending['before'][dest]['totals'];quantity=pending['before'][source]['totals']
   expected=copy.deepcopy(before)
   for k,v in quantity.items():expected[k]=expected.get(k,0)+amount*v
   for k in set(expected)|set(fail['expected']['totals']):assert abs(expected.get(k,0)-fail['expected']['totals'].get(k,0))<1e-8
   fresh=next(c['observed'] for c in pending['checks'] if c['instance']==source);assert fresh['totals']==quantity
   r.update(task_id=pending['task_id'],amount=amount,recipe_totals=quantity,before=before,expected=fail['expected'],observed=fail['observed'],merges_completed=sum(t['kind']=='semantic_merge' for t in rs),mutation_request=next(l for l in reversed(lines[:lines.index(warning)]) if 'Selected: [POST' in l))
  out.append(r)
(Path(__file__).parent/'verification-result.json').write_text(json.dumps(out,indent=2))
for r in out:
 if 'amount' in r:
  print(r['case'],r['sample'],'AMOUNT',r['amount'],'BEFORE',list(r['before'].values()),'RECIPE',list(r['recipe_totals'].values()),'EXPECTED',list(r['expected']['totals'].values()),'ACTUAL',list(r['observed']['totals'].values()),'MERGES',r['merges_completed'],'REFS_OK',r['expected']['references']==r['observed']['references'])
 else:print(r['case'],r['sample'],'PASS','HTTP',r['http_responses'],'FINAL',r['final_manual_totals'])
for case in sorted({r['case'] for r in out}):
 pair=[r for r in out if r['case']==case]
 print(case,'distinct orders',pair[0]['completed_order']!=pair[1]['completed_order'],'disjoint resources',not(set(pair[0]['resource_ids'])&set(pair[1]['resource_ids'])))
