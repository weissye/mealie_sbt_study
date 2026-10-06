"""Extract credential-free F01 callback receipts from a completed native log."""
import argparse,hashlib,json,re,zipfile
from pathlib import Path
from native_log_text import decode_native_log
p=argparse.ArgumentParser();p.add_argument('--project',required=True);a=p.parse_args();root=Path(a.project)
raw=(root/'native-run.log').read_bytes();text=decode_native_log(raw);stages=[];receipts=[]
for line in text.splitlines():
 if 'F01_RECEIPT ' in line:receipts.append(json.loads(line.split('F01_RECEIPT ',1)[1]))
 if 'F01_EVIDENCE ' in line:
  payload=line.split('F01_EVIDENCE ',1)[1];stages.append(json.loads(payload))
completed='Selected: [F01Completed]' in text and 'Test Result: SUCCESS' in text
candidate=bool(stages and stages[-1]['issues'])
status='F01_SEMANTIC_CANDIDATE' if candidate else 'F01_FUNCTIONAL_PASS' if completed and len(stages)==2 else 'F01_INCOMPLETE'
report={'status':status,'completed':completed,'native_provengo_executed':True,'sut_run_claim':'Run target and source are recorded in generated files; this collector does not authenticate target identity','new_bug_confirmed':False,'receipts':receipts,'review':stages[-1] if stages else None,'native_log_sha256':hashlib.sha256(raw).hexdigest(),'raw_log_included':False}
(root/'qualification.json').write_text(json.dumps(report,indent=2))
with zipfile.ZipFile(root/'review.zip','w',zipfile.ZIP_DEFLATED) as z:
 for directory in ('spec/js','config'):
  for file in (root/directory).rglob('*'):
   if file.is_file() and file.suffix in ('.js','.json','.yml'):z.write(file,file.relative_to(root))
 z.write(root/'qualification.json','qualification.json')
print(status);print('Review ZIP: '+str(root/'review.zip'))
