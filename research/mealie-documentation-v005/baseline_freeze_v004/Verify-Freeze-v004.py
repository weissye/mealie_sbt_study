import argparse,hashlib,json,pathlib,zipfile,re,ast
BASE=pathlib.Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def audit(source):
 pin=json.loads((BASE/'BASELINE_v004.json').read_text());assert sha(source.read_bytes())==pin['source_zip_sha256'],'Source archive differs from frozen baseline'
 with zipfile.ZipFile(source) as z:
  root='final_package/';m=json.loads(z.read(root+'EVIDENCE_MANIFEST.json'));bad=[]
  for n,s in m['sha256'].items():
   if sha(z.read(root+n))!=s:bad.append(n)
  assert not bad,('Source hash failures',bad)
  assert len(m['sha256'])==m['file_count']==415
  nested=[]
  for version in range(7,17):
   prefix=root+'evidence/v%03d/'%version;d=json.loads(z.read(prefix+'manifest_v%03d.json'%version));hs=d.get('sha256',d)
   for n,s in hs.items():assert sha(z.read(prefix+n.replace('\\','/')))==s,(version,n)
   nested.append({'version':'v%03d'%version,'hashes':len(hs)})
  prefix=root+'generator/';templates=json.loads(z.read(prefix+'delta/generator_v56/package_templates_v016.json'));matches=[]
  for name,body in templates.items():
   n=name.replace('__VU__','V016').replace('__V__','v016');expected=body.replace('__VU__','V016').replace('__V__','v016').encode()
   matches.append({'file':n,'bytes_match':z.read(prefix+n)==expected})
  assert all(r['bytes_match'] for r in matches),'Template/output drift'
  syntax=[]
  for n in z.namelist():
   if n.startswith(prefix) and n.endswith('.py'):ast.parse(z.read(n).decode('utf-8-sig'),filename=n);syntax.append(n[len(prefix):])
  result=json.loads(z.read(root+'evidence/v016/result_v016.json'))
  assert result['status']=='V016_LIVE_BOUNDARY_RUN_COMPLETE' and result['provengo_exit']==0 and result['generated_steps']==15
  assert len(result['markers'])==15 and len(set(result['markers']))==15 and result['native_test_result_success'] is True
  report=json.loads(z.read(root+'evidence/v016/project/generation_report_v016.json'))
  c=sha(z.read(prefix+'delta/generator_v56/boundary_plan_v016.py'))
  assert result['compiler_sha256']==c
  contract_bytes=z.read(prefix+'contract/mealie-openapi.v3.28.0.live-v007.json')
  contract_hash_canonical=sha(json.dumps(json.loads(contract_bytes),sort_keys=True).encode())
  assert report['contract_sha256']==contract_hash_canonical
  allfiles=[n for n in z.namelist() if not n.endswith('/')];raw=[]
  for n in allfiles:
   if re.search(rb'eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}',z.read(n)):raw.append(n)
  return {'version':'v004','source_hash_verified':True,'master_manifest_hashes':415,'nested_manifests':nested,'template_output_matches':matches,'python_syntax_files':syntax,'v016_native_receipt_status':result['status'],'v016_markers':result['markers'],'v016_compiler_matches_receipt':True,'v016_contract_matches_report':True,'contract_file_sha256':sha(contract_bytes),'contract_canonical_json_sha256':contract_hash_canonical,'raw_jwt_pattern_matches':raw,'method':'Read-only ZIP, text and AST audit; no imports, generation or live requests','limits':['Existing receipt is audited, not a new live run','Template bytes match existing outputs; full package regeneration not executed','Pattern scan is not a proof of absence of every possible secret','Semantic intent is explicitly authored; OpenAPI-only semantic discovery not established']}
def main():
 a=argparse.ArgumentParser();a.add_argument('--source',type=pathlib.Path,required=True);a.add_argument('--write-audit',type=pathlib.Path);args=a.parse_args()
 manifest=json.loads((BASE/'FREEZE_MANIFEST_v004.json').read_text()) if (BASE/'FREEZE_MANIFEST_v004.json').exists() else None
 if manifest:
  for n,s in manifest['sha256'].items():assert sha((BASE/n).read_bytes())==s,('Freeze hash failure',n)
 result=audit(args.source)
 if args.write_audit:args.write_audit.write_text(json.dumps(result,indent=2)+'\n')
 print('MEALIE_FREEZE_V004_ACCEPTED',result['master_manifest_hashes'],'original hashes;',len(result['template_output_matches']),'template matches;',len(result['python_syntax_files']),'Python syntax files')
if __name__=='__main__':main()
