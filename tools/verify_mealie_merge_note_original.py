"""Read-only verification of the archived note-order false positive."""
import hashlib,json,zipfile
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parents[1]
evidence=root/'evidence/merge-note-order-20261006-070250'
meta=json.loads((evidence/'qualification.json').read_text(encoding='utf-8-sig'))
archive=evidence/'review-original.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==meta['archive_sha256'],'Archive checksum differs'
with zipfile.ZipFile(archive) as z:
    report=json.loads(z.read('acceptance-report.json'))
    receipts=json.loads(z.read('response-receipts.json'))
    assert report['scenario']=='merge' and report['native_exit_code']==1
    assert len(receipts)==39 and receipts[-1]['operation']=='depMergeAdd'
    before=[x['body'] for x in receipts if x['operation']=='depVerifychild1update'][-1]
    envelope=receipts[-1]['body'];got=envelope['updatedItems'][0]
    assert envelope['createdItems']==[] and envelope['deletedItems']==[] and len(envelope['updatedItems'])==1
    assert all(got[k]==before[k] for k in ('id','shoppingListId','foodId','unitId'))
    assert got['quantity']==before['quantity']+2==3
    expected=before['note']+' | '+report['namespace']+'-merge-contribution'
    assert got['note']!=expected and Counter(got['note'].split(' | '))==Counter(expected.split(' | '))
    assert not any(x['operation'] in ('depMergeReadback','depMergeParentReadback') for x in receipts)
    assert 'FAIL: MERGE_RESPONSE_STATE_MISMATCH' in z.read('live-output.txt').decode()
print('MERGE_NOTE_ORDER_ORIGINAL_QUALIFIED: response identity, quantity and dependencies correct; note components reordered; no independent post-merge GET reached. No API requests sent.')
