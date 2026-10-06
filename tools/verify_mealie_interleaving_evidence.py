"""Read-only independent validation of the archived real Mealie acceptance."""
import hashlib,json,re,zipfile
from pathlib import Path

def verify(root):
    directory=root/'evidence/generator-interleaving-20261006-051538'
    archive=directory/'review-original.zip'
    expected=(directory/'SHA256.txt').read_text().split()[0]
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected:raise ValueError('Evidence checksum differs')
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('ZIP integrity failed')
        if any('products' in n.split('/') for n in z.namelist()):raise ValueError('Private authentication products included')
        report=json.loads(z.read('acceptance-report.json'));receipts=json.loads(z.read('response-receipts.json'));writes=json.loads(z.read('write-receipts.json'))
        if report['status']!='NATIVE_INTERLEAVED_DEPENDENCY_PASS' or report['native_exit_code']!=0 or len(receipts)!=24 or len(writes)!=4:raise ValueError('Acceptance incomplete')
        def rows(op):return [x['body'] for x in receipts if x['operation']==op]
        parents={i:rows('depCreateparent'+str(i))[0] for i in (1,2)}
        children={i:rows('depCreatechild'+str(i))[0]['createdItems'][0] for i in (1,2)}
        if len({x['id'] for x in children.values()})!=2:raise ValueError('Child identities ambiguous')
        if {x['shoppingListId'] for x in children.values()}!={parents[2]['id']}:raise ValueError('Shared binding differs')
        for i,child in children.items():
            final=rows('depVerifychild'+str(i)+'update')
            if len(final)!=2:raise ValueError('Final child reads absent')
            for x in final:
                for field in ('id','shoppingListId','quantity','position','checked','groupId','householdId'):
                    if x[field]!=child[field]:raise ValueError('Child state differs: '+field)
                if x['note']!=child['note']+'-updated':raise ValueError('Child marker mismatch')
        ids={x['id'] for x in children.values()}
        sent=next(x['body'] for x in writes if x['operation']=='depUpdateparent2')
        if {x['id'] for x in sent['listItems']}!=ids:raise ValueError('Submitted collection incomplete')
        for op in ('depUpdateparent2','depVerifyparent2update','depMembershipchild1','depMembershipchild2'):
            for x in rows(op):
                if {a['id'] for a in x['listItems']}!=ids and op in ('depUpdateparent2','depVerifyparent2update'):raise ValueError('Parent lost child')
        log=z.read('live-output.txt').decode()
        if len(re.findall(r'Selected: \[(GET|POST|PUT|PATCH|DELETE) ',log))!=25:raise ValueError('HTTP call count differs')
        if 'Test Fail Mode' in log:raise ValueError('Live fail mode present')
        if z.read('model/spec/js/stories.mealie.js').decode().count('bthread(')!=18:raise ValueError('Architecture count differs')
    return {'status':'REAL_INTERLEAVING_EVIDENCE_VERIFIED','http_calls':25,'business_responses':24,'bthreads':18,'new_bug_confirmed':False,'resource_mutations_sent_by_verifier':0}

if __name__=='__main__':
    print(json.dumps(verify(Path(__file__).resolve().parents[1]),indent=2))
