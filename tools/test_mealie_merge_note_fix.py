"""Renderer patch compatibility and archived-callback regression tests.
Node executes captured JS callbacks with local RTV/HTTP stubs; this is not a live or native replay.
"""
import copy,hashlib,json,shutil,subprocess,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from native_merge_note_policy import repair_interfaces,repair_renderer,WRAPPER_MARKER
from apply_mealie_merge_note_fix import apply
ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/'evidence/merge-note-order-20261006-070250/review-original.zip'

class NoteFixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(ARCHIVE) as z:
            cls.source=z.read('model/spec/js/interfaces.mealie.js').decode()
            receipts=json.loads(z.read('response-receipts.json'))
        cls.before=[x['body'] for x in receipts if x['operation']=='depVerifychild1update'][-1]
        cls.merged=receipts[-1]['body']
        cls.other=[x['body'] for x in receipts if x['operation']=='depVerifychild2update'][-1]
        cls.parent=[x['body'] for x in receipts if x['operation']=='depMembershipchild1'][-1]
    def test_three_exact_callback_anchors(self):
        fixed=repair_interfaces(self.source,'note',' | ')
        self.assertEqual(fixed.count('!depMergeNotesEqual('),3)
        self.assertIn('obj["quantity"]!==expected.quantity',fixed)
        self.assertIn('obj["id"]!==expected.id',fixed)
        self.assertIn('MERGE_PARENT_VIEW_MISMATCH',fixed)
    def test_incompatible_source_stops(self):
        with self.assertRaises(ValueError):repair_interfaces(self.source.replace('obj["note"]!==note','true',1),'note',' | ')
    def test_distinct_renderer_unchanged(self):
        original=lambda:('interfaces','stories',{'scenario':'distinct'})
        self.assertEqual(repair_renderer(original)(),original())
    def test_explicit_policy_required(self):
        original=lambda:('interfaces','stories',{'scenario':'merge','merge_policy':{},'workers':[{'role':'child','marker_field':'note'}]})
        with self.assertRaises(ValueError):repair_renderer(original)()
    def test_installer_is_idempotent_and_preserves_backup(self):
        # Exercise exact CRLF fixture bytes and emulate Windows text writes even on Linux.
        original_write_text=Path.write_text
        def windows_write_text(path,data,*args,**kwargs):
            kwargs['newline']='\r\n'
            return original_write_text(path,data,*args,**kwargs)
        for ending in (b'\n',b'\r\n'):
            with self.subTest(line_ending=repr(ending)), tempfile.TemporaryDirectory() as folder:
                root=Path(folder)
                for directory in ('tools','profiles','validation'):(root/directory).mkdir()
                source=root/'tools/render_native_distinct_merge.py'
                source.write_bytes(b'def render():\n    # depMergeAdd depMergeReadback depMergeParentReadback\n    return None\n'.replace(b'\n',ending))
                policy=root/'profiles/mealie-native-merge-policy.json'
                policy.write_bytes((json.dumps({'quantity_rule':'sum','identity_rule':'retain_existing','note_separator':' | '},indent=2)+'\n').encode().replace(b'\n',ending))
                original=source.read_bytes()
                entries={p.relative_to(root).as_posix():{'normalization':'LF','sha256':hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()} for p in (source,policy)}
                (root/'validation/mealie-native-distinct-merge-release.json').write_bytes(json.dumps({'files':entries}).encode())
                with patch.object(Path,'write_text',windows_write_text):
                    apply(root);after=source.read_bytes();apply(root)
                self.assertIn(b'\r\n',after)
                self.assertEqual(source.read_bytes(),after);self.assertEqual(after.decode().count(WRAPPER_MARKER),1)
                backups=list((root/'runs').glob('merge-note-source-backup-*'))
                self.assertEqual(len(backups),1);self.assertEqual((backups[0]/source.name).read_bytes(),original)
    @unittest.skipUnless(shutil.which('node'),'Node is optional; archived callback tests validated in release environment')
    def test_archived_javascript_callbacks(self):
        fixed=repair_interfaces(self.source,'note',' | ')
        parent=copy.deepcopy(self.parent);parent['listItems']=[self.merged['updatedItems'][0]]
        data={'source':fixed,'before':self.before,'response':self.merged,'other':self.other,'parent':parent}
        harness=r'''
const fs=require('fs'),vm=require('vm');const data=JSON.parse(fs.readFileSync(0,'utf8'));
let runs=0;
function execute(edit,expectedFailure){
  const copy=JSON.parse(JSON.stringify(data)),values={'dep_child1_snapshot':JSON.stringify(copy.before)};
  const other=copy.other;
  values.dep_child2_id=other.id;values.dep_child2_parent=other.shoppingListId;
  values.dep_child2_foodId=other.foodId;values.dep_child2_unitId=other.unitId;
  values.dep_child2_scalar_baseline=JSON.stringify(Object.fromEntries(Object.entries(other).filter(([k,v])=>typeof v==='number'||typeof v==='boolean')));
  let reply;
  const context={bp:{log:{info:()=>{}}},pvg:{rtv:{get:k=>values[k],set:(k,v)=>{values[k]=v;}},fail:m=>{throw new Error(m)},success:()=>{}},RESTSession:function(){for(const method of ['post','get','put','delete','patch'])this[method]=(url,options)=>options.callback({body:JSON.stringify(reply)});}};
  vm.createContext(context);vm.runInContext(copy.source,context);edit(copy);
  try{
    reply=copy.response;context.depMergeAdd();
    reply=copy.persisted||copy.response.updatedItems[0];context.depMergeReadback();
    reply=copy.parent;context.depMergeParentReadback();
    reply=copy.other;context.depVerifychild2update();
    if(expectedFailure)throw new Error('Expected failure was not detected');
  }catch(e){if(!expectedFailure||!e.message.includes(expectedFailure))throw e;}
  runs++;
}
execute(()=>{},null); // Actual server response: new note before old note.
execute(c=>{c.response.updatedItems[0].note=c.response.updatedItems[0].note.split(' | ').reverse().join(' | ');},null);
execute(c=>{c.response.updatedItems[0].note=c.before.note;},'MERGE_RESPONSE_STATE_MISMATCH');
execute(c=>{c.response.updatedItems[0].note=c.before.note+' | '+c.before.note;},'MERGE_RESPONSE_STATE_MISMATCH');
execute(c=>{c.response.updatedItems[0].note+=' | '+c.before.note;},'MERGE_RESPONSE_STATE_MISMATCH');
execute(c=>{c.response.updatedItems[0].quantity=4;},'MERGE_RESPONSE_STATE_MISMATCH');
execute(c=>{c.response.updatedItems[0].foodId='different';},'MERGE_RESPONSE_STATE_MISMATCH');
execute(c=>{c.parent.listItems[0].quantity=4;},'MERGE_PARENT_VIEW_MISMATCH');
execute(c=>{c.other.quantity=2;},'Scalar state changed after marker update');
execute(c=>{c.persisted=c.before;},'MERGE_PERSISTED_STATE_MISMATCH');
execute(c=>{c.persisted=JSON.parse(JSON.stringify(c.response.updatedItems[0]));c.persisted.note=c.before.note;},'MERGE_PERSISTED_STATE_MISMATCH');
console.log(JSON.stringify({archived_callback_cases:runs,status:'PASS',scope:'Local JavaScript callbacks with stubs; no API requests or native replay'}));
'''
        result=subprocess.run(['node','-e',harness],input=json.dumps(data),text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(json.loads(result.stdout)['archived_callback_cases'],11)

if __name__=='__main__':unittest.main()
