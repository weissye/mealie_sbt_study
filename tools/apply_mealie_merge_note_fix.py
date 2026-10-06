"""Install an additive native renderer wrapper; preserve existing source bytes."""
import argparse,hashlib,json
from datetime import datetime
from pathlib import Path
from native_merge_note_policy import WRAPPER_MARKER,WRAPPER_SUFFIX

def apply(root):
    source=root/'tools/render_native_distinct_merge.py'
    profile=root/'profiles/mealie-native-merge-policy.json'
    release=root/'validation/mealie-native-distinct-merge-release.json'
    original={p:p.read_bytes() for p in (source,profile,release)}
    text=original[source].decode('utf-8-sig')
    policy=json.loads(original[profile].decode('utf-8-sig'))
    report=json.loads(original[release].decode('utf-8-sig'))
    if 'def render(' not in text or 'depMergeAdd' not in text or 'depMergeReadback' not in text or 'depMergeParentReadback' not in text:raise ValueError('Expected native merge renderer is not installed')
    if policy.get('quantity_rule')!='sum' or policy.get('identity_rule')!='retain_existing' or policy.get('note_separator')!=' | ':raise ValueError('Installed policy differs from the qualified experiment')
    for path in (source,profile):
        name=path.relative_to(root).as_posix();record=report['files'].get(name)
        if record is None:raise ValueError('Original release checksum entry missing: '+name)
        raw=original[path];digest=hashlib.sha256(raw.replace(b'\r\n',b'\n') if record['normalization']=='LF' else raw).hexdigest()
        if digest!=record['sha256']:raise ValueError('Installed source differs from its release checksum: '+name)
    if WRAPPER_MARKER in text:
        if text.count(WRAPPER_MARKER)!=1 or not text.replace('\r\n','\n').endswith(WRAPPER_SUFFIX) or policy.get('note_comparison')!='unordered_multiset':raise ValueError('Existing repair is incomplete or differs')
        print('MERGE_NOTE_FIX_ALREADY_INSTALLED');return
    stamp=datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup=root/'runs'/('merge-note-source-backup-'+stamp);backup.mkdir(parents=True)
    for path,raw in original.items():(backup/path.name).write_bytes(raw)
    # All compatibility checks completed before touching the installed files.
    source.write_text(text.replace('\r\n','\n')+WRAPPER_SUFFIX,encoding='utf-8')
    policy['note_comparison']='unordered_multiset'
    policy['note_order_qualification']='Both contribution notes and their exact multiplicities are required; their concatenation order is not constrained.'
    profile.write_text(json.dumps(policy,indent=2)+'\n',encoding='utf-8')
    for path in (source,profile):
        name=path.relative_to(root).as_posix();record=report['files'][name];record['sha256']=hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest();record['normalization']='LF'
    report['merge_note_fix']='Additive wrapper; original quantity/identity/dependency checks retained; note order corrected separately from original evidence.'
    release.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('MERGE_NOTE_FIX_INSTALLED; original source backup:',backup)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);a=p.parse_args();apply(a.root.resolve())
