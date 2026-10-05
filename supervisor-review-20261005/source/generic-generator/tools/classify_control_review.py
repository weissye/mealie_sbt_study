"""Classify preserved native evidence without sending server requests."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

def classify(path):
    with zipfile.ZipFile(path) as archive:
        acceptance = json.loads(archive.read('execution-review/run-acceptance.json').decode('utf-8-sig'))
        lines = archive.read('execution-review/run-output.txt').decode('utf-8-sig').splitlines()
    result = {'review': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'status': 'BLOCKED', 'new_bug_confirmed': False, 'server_requests': 0}
    if acceptance.get('live_accepted') is True:
        result['status'] = 'PASS'
    else:
        failures = [line for line in lines if ' WARN [' in line and 'FAIL: Semantic consistency mismatch: ' in line]
        if failures:
            payload = failures[0].split('FAIL: Semantic consistency mismatch: ', 1)[1].removesuffix('.')
            result.update(status='SEMANTIC_CANDIDATE', first_failure=json.loads(payload))
        else:
            result['reason'] = acceptance.get('error', 'No accepted run or semantic discrepancy evidence.')[:1000]
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--review', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = classify(Path(args.review))
    Path(args.output).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(result['status'])
    raise SystemExit(3 if result['status'] == 'BLOCKED' else 0)
