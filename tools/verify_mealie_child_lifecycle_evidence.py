"""Independent read-only checks of the archived real Mealie deletion acceptance."""
import hashlib,json,re,zipfile
from pathlib import Path

def verify(root):
    directory=root/'evidence/generator-child-lifecycle-20261006-052852'
    archive=directory/'review-original.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=(directory/'SHA256.txt').read_text().split()[0]:raise ValueError('Evidence checksum differs')
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('ZIP integrity failed')
        if any('products' in x.split('/') for x in z.namelist()):raise ValueError('Private authentication products present')
        report=json.loads(z.read('acceptance-report.json'));r=json.loads(z.read('response-receipts.json'))
        if report['status']!='NATIVE_CHILD_LIFECYCLE_PASS' or report['native_exit_code']!=0 or len(r)!=28:raise ValueError('Acceptance incomplete')
        def rows(op):return [x['body'] for x in r if x['operation']==op]
        first=rows('depCreatechild1')[0]['createdItems'][0];second=rows('depCreatechild2')[0]['createdItems'][0]
        parent=rows('depVerifyDeletionParent')[0];before=rows('depVerifyparent2update')[0];survivor=rows('depVerifychild2update')[-1]
        if [x['id'] for x in parent['listItems']]!=[second['id']]:raise ValueError('Deletion membership differs')
        if first['shoppingListId']!=second['shoppingListId'] or parent['id']!=second['shoppingListId']:raise ValueError('Parent binding differs')
        for field in ('id','name','userId','groupId','householdId'):
            if parent[field]!=before[field]:raise ValueError('Parent state differs: '+field)
        for field in ('id','shoppingListId','quantity','position','checked','groupId','householdId'):
            if survivor[field]!=second[field]:raise ValueError('Survivor state differs: '+field)
        if survivor['note']!=second['note']+'-updated':raise ValueError('Survivor note differs')
        sample=json.loads(z.read('samples.json'))[0]
        negative=[e for e in sample if e.get('name')=='GET' and 'dep_child1_id' in e.get('data',{}).get('url','') and e['data'].get('expectedResponseCodes')==[404]]
        if len(negative)!=1 or len(rows('depVerifyDeletedchild1'))!=1:raise ValueError('Negative read evidence absent')
        log=z.read('live-output.txt').decode();http=re.findall(r'Selected: \[(GET|POST|PUT|PATCH|DELETE) ',log)
        if len(http)!=29 or http.count('DELETE')!=1 or 'Test Fail Mode' in log:raise ValueError('Live execution differs')
    return {'status':'REAL_CHILD_LIFECYCLE_EVIDENCE_VERIFIED','http_calls':29,'business_responses':28,'new_bug_confirmed':False,'api_requests_sent_by_verifier':0}
if __name__=='__main__':print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
