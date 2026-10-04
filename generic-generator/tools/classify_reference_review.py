"""Read-only classification. A candidate is not a confirmed new bug."""
import argparse,hashlib,json,zipfile,re
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.reference_receipts import validate_reference_receipts
from tools.transfer_receipts import validate_transfer_receipts
from tools.route_receipts import validate_route_receipts


def classify(path):
    with zipfile.ZipFile(path) as archive:
        acceptance=json.loads(archive.read('execution-review/run-acceptance.json').decode('utf-8-sig'))
        output=archive.read('execution-review/run-output.txt').decode('utf-8-sig')
        plan=json.loads(archive.read('relationship_scenario_plan.json').decode('utf-8-sig'))
    result={'status':'BLOCKED','review':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'new_bug_confirmed':False,'server_requests_sent_by_classifier':0}
    if acceptance.get('live_accepted') is True:
        receipt=acceptance.get('runtime_receipt',{})
        validate_reference_receipts(receipt,plan)
        validate_transfer_receipts(receipt,plan)
        validate_route_receipts(receipt,plan)
        result.update(status='PASS',outcomes=[r['outcome'] for r in receipt.get('reference_lifecycles',[])])
    else:
        route_failures=[line for line in output.splitlines() if ' WARN [' in line and 'FAIL: Route identity mismatch: ' in line]
        if route_failures:
            result.update(status='ROUTE_CANDIDATE',first_failure=json.loads(route_failures[0].split('FAIL: Route identity mismatch: ',1)[1].removesuffix('.')))
            return result
        transfer_failures=[line for line in output.splitlines() if ' WARN [' in line and 'FAIL: Dependency transfer mismatch: ' in line]
        if transfer_failures:
            payload=transfer_failures[0].split('FAIL: Dependency transfer mismatch: ',1)[1].removesuffix('.')
            result.update(status='TRANSFER_CANDIDATE',first_failure=json.loads(payload))
            return result
        failures=[line for line in output.splitlines() if ' WARN [' in line and 'FAIL: Reference lifecycle mismatch: ' in line]
        if failures:
            payload=failures[0].split('FAIL: Reference lifecycle mismatch: ',1)[1].removesuffix('.')
            evidence=json.loads(payload)
            result.update(status='POLICY_OBSERVATION' if evidence.get('stage')=='stale_success_requires_policy_qualification' else 'REFERENCE_CANDIDATE',first_failure=evidence)
        else:
            # A server error is a candidate only when associated with a selected
            # non-authentication REST operation. No success receipt is inferred.
            lines=output.splitlines();selected=None
            for line in lines:
                if 'Selected: [' in line and 'lib:"REST"' in line:selected=line
                if re.search(r'actual 5\d\d, expected:',line) and selected and '/auth/token' not in selected:
                    result.update(status='SERVER_ERROR_CANDIDATE',first_failure={'selected_operation':selected[-1500:],'http_failure':line[:500]});break
            if result['status']=='BLOCKED':result['reason']=acceptance.get('error','Authentication, transport, HTTP status or unclassified failure; inspect the review.')[:1000]
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--review',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    result=classify(Path(args.review));Path(args.output).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(result['status']);raise SystemExit(3 if result['status']=='BLOCKED' else 0)
