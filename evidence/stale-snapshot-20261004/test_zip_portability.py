"""Exercise the exact verifier helper with ZIP member names from both platforms."""
import ast,io,unittest,zipfile
from pathlib import Path
source=Path(__file__).with_name('verify_campaign.py').read_text()
node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='read_member')
namespace={}
exec(compile(ast.Module(body=[node],type_ignores=[]),'verify_campaign.py','exec'),namespace)
read_member=namespace['read_member']
class ZipPortabilityTests(unittest.TestCase):
 def test_forward_backward_and_repeated_separators(self):
  for stored in ['food-control/result-1.json','food-control'+chr(92)+'result-1.json','food-control'+chr(92)*2+'result-1.json']:
   buffer=io.BytesIO()
   with zipfile.ZipFile(buffer,'w') as archive:archive.writestr(stored,b'expected')
   with zipfile.ZipFile(io.BytesIO(buffer.getvalue())) as archive:
    self.assertEqual(read_member(archive,'food-control/result-1.json'),b'expected')
 def test_nested_archive_names(self):
  buffer=io.BytesIO()
  with zipfile.ZipFile(buffer,'w') as archive:archive.writestr('execution-review'+chr(92)+'run-acceptance.json',b'{}')
  with zipfile.ZipFile(io.BytesIO(buffer.getvalue())) as archive:self.assertEqual(read_member(archive,'execution-review/run-acceptance.json'),b'{}')
 def test_ambiguous_alias_is_rejected(self):
  buffer=io.BytesIO()
  with zipfile.ZipFile(buffer,'w') as archive:
   archive.writestr('a/b',b'first');archive.writestr('a'+chr(92)+'b',b'second')
  with zipfile.ZipFile(io.BytesIO(buffer.getvalue())) as archive:
   with self.assertRaises(ValueError):read_member(archive,'a/b')
 def test_missing_member_is_rejected(self):
  buffer=io.BytesIO()
  with zipfile.ZipFile(buffer,'w'):pass
  with zipfile.ZipFile(io.BytesIO(buffer.getvalue())) as archive:
   with self.assertRaises(ValueError):read_member(archive,'missing')
if __name__=='__main__':unittest.main()
