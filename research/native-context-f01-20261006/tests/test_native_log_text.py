import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from native_log_text import decode_native_log
class NativeLogTests(unittest.TestCase):
 def test_realistic_log_is_preserved_in_all_supported_encodings(self):
  text='Test Result: SUCCESS\r\nF01_EVIDENCE {"issues":[],"name":"עברית"}\r\n'
  for raw in (text.encode('utf-8'),text.encode('utf-8-sig'),b'\xff\xfe'+text.encode('utf-16-le'),b'\xfe\xff'+text.encode('utf-16-be')):
   with self.subTest(prefix=raw[:3]):self.assertEqual(decode_native_log(raw),text)
 def test_invalid_unmarked_bytes_are_rejected(self):
  with self.assertRaises(UnicodeDecodeError):decode_native_log(b'\x80\xffinvalid')
if __name__=='__main__':unittest.main()
