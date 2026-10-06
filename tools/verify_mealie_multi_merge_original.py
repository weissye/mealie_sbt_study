"""Read-only qualification of the original multi-dependency stop."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
evidence=ROOT/'evidence/generator-multi-merge-20261006-054723'
expected=json.loads((evidence/'qualification.json').read_text(encoding='utf-8-sig'))
archive=evidence/'review-original.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected['archive_sha256'],'Archive checksum mismatch'
with zipfile.ZipFile(archive) as z:
    receipts=json.loads(z.read('response-receipts.json'))
    report=json.loads(z.read('acceptance-report.json'))
    assert report['native_exit_code']==1
    assert len(receipts)==27 and receipts[-1]['operation']=='depCreatechild1'
    first=next(x['body']['createdItems'][0] for x in receipts if x['operation']=='depCreatechild2')
    before=[x['body'] for x in receipts if x['operation']=='depObservechild2'][-1]
    response=receipts[-1]['body']
    assert response['createdItems']==[] and response['deletedItems']==[] and len(response['updatedItems'])==1
    merged=response['updatedItems'][0]
    assert first['id']==before['id']==merged['id']
    assert before['quantity']==1 and merged['quantity']==2
    assert all(before[k]==merged[k] for k in ('shoppingListId','foodId','unitId'))
    assert 'Create envelope identity ambiguous' in z.read('live-output.txt').decode()
print('ORIGINAL_MULTI_MERGE_QUALIFIED: merge shown in POST response; no independent post-merge GET; no new bug confirmed. No API requests sent.')
