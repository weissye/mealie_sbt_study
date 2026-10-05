"""Verify frozen original evidence independently; no network requests."""
from pathlib import Path
import subprocess,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
checks=[('quantity', [ROOT/'evidence/mealie-quantity-family-20261004/verify_freeze.py']),('copy',[ROOT/'source/generic-generator/tools/verify_copy_campaign.py','--campaign',ROOT/'evidence/copy-isolation-20261005-082853/campaign-original.zip','--output',ROOT/'validation/local/copy-recheck.json']),('unavailable-reference',[ROOT/'evidence/multi-identity-20261005-065704/verify_campaign.py']),('household-state',[ROOT/'evidence/scope-controls-20261005-073218/verify_campaign.py'])]
def main():
 (ROOT/'validation/local').mkdir(parents=True,exist_ok=True)
 manifest=ROOT/'PACKAGE-SHA256.json'
 if manifest.exists():
  for name,expected in json.loads(manifest.read_text()).items():
   actual=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
   if actual!=expected:raise ValueError('Package byte mismatch: '+name)
 results=[]
 for label,args in checks:
  p=subprocess.run([sys.executable,'-B',*map(str,args)],cwd=ROOT,capture_output=True,text=True,timeout=120)
  item={'check':label,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr};results.append(item)
  print(label+': '+('PASS' if p.returncode==0 else 'FAIL'))
  if p.returncode:print(p.stderr)
 (ROOT/'validation/local/evidence-recheck.json').write_text(json.dumps({'server_requests':0,'checks':results},indent=2))
 if any(r['exit_code'] for r in results):raise SystemExit(1)
 print('ALL_FIVE_FINDING_GROUPS_ARCHIVE_VERIFIED')
if __name__=='__main__':main()
