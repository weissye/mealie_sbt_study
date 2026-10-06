"""Order-independent note multiplicity checks for the native merge renderer.
All HTTP and verifier scheduling remain in the existing native model.
"""
import functools,json

WRAPPER_MARKER = '# Native merge note policy: unordered multiplicity v1'
WRAPPER_SUFFIX = '\n\n' + WRAPPER_MARKER + '\nfrom native_merge_note_policy import repair_renderer as _repair_merge_note_renderer\nrender = _repair_merge_note_renderer(render)\n'

JS_HELPER = '''
function depMergeNotesEqual(actual,expected,separator){
  if(typeof actual!=="string"||typeof expected!=="string"||typeof separator!=="string"||separator.length===0)return false;
  var got=actual.split(separator).sort(),want=expected.split(separator).sort();
  if(got.length!==want.length)return false;
  for(var i=0;i<got.length;i++){if(got[i]!==want[i])return false;}
  return true;
}
'''

def repair_interfaces(interfaces, marker_field, separator):
    if not isinstance(separator,str) or not separator:raise ValueError('A nonempty explicit note separator is required')
    q=json.dumps
    checks={
        'depMergeAdd': ('obj['+q(marker_field)+']!==note', '!depMergeNotesEqual(obj['+q(marker_field)+'],note,'+q(separator)+')'),
        'depMergeReadback': ('obj['+q(marker_field)+']!==expected.note', '!depMergeNotesEqual(obj['+q(marker_field)+'],expected.note,'+q(separator)+')'),
        'depMergeParentReadback': ('items[0]['+q(marker_field)+']!==expected.note', '!depMergeNotesEqual(items[0]['+q(marker_field)+'],expected.note,'+q(separator)+')')
    }
    lines=interfaces.splitlines();seen=set()
    for index,line in enumerate(lines):
        for fn,(old,new) in checks.items():
            if not line.startswith('function '+fn+'('):continue
            if fn in seen or line.count(old)!=1:raise ValueError('Expected verifier anchor differs: '+fn)
            lines[index]=line.replace(old,new,1);seen.add(fn)
    if seen!=set(checks):raise ValueError('Missing native merge verifier functions')
    if 'function depMergeNotesEqual(' in interfaces:raise ValueError('Merge note helper already present')
    return '\n'.join(lines)+'\n'+JS_HELPER

def repair_renderer(original):
    @functools.wraps(original)
    def render(*args,**kwargs):
        interfaces,stories,manifest=original(*args,**kwargs)
        if manifest.get('scenario')!='merge':return interfaces,stories,manifest
        policy=manifest.get('merge_policy') or {}
        if policy.get('note_comparison')!='unordered_multiset':raise ValueError('Explicit unordered_multiset merge note policy required')
        markers={w['marker_field'] for w in manifest['workers'] if w.get('role')=='child'}
        if len(markers)!=1:raise ValueError('Merge marker field is ambiguous')
        interfaces=repair_interfaces(interfaces,next(iter(markers)),policy.get('note_separator'))
        manifest['merge_note_qualification']='Exact components and multiplicities; ordering is not constrained. Quantity, identity, dependencies and independent GET checks remain unchanged.'
        return interfaces,stories,manifest
    return render
