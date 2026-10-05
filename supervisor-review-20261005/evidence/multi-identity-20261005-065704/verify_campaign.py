"""Verify the frozen campaign without contacting Mealie or changing files."""
import ast
import hashlib
import io
import json
from pathlib import Path
import zipfile
from qualification_oracle import IdentityMismatch, validate_identity_receipts


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(root):
    checks = json.loads((root / 'checksums.json').read_text(encoding='utf-8-sig'))
    for name, expected in checks.items():
        require(Path(name).name == name, 'Invalid evidence checksum path.')
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == expected,
                'Evidence checksum mismatch: ' + name)
    qualified = json.loads((root / 'qualification.json').read_text(encoding='utf-8-sig'))
    total = 0
    namespaces = set()
    with zipfile.ZipFile(root / 'campaign-original.zip') as campaign:
        require(campaign.testzip() is None, 'Campaign ZIP CRC failure.')
        summary = json.loads(campaign.read('campaign-summary.json'))
        require(len(summary['runs']) == 4, 'Expected exactly four runs.')
        require({(r['case'], r['sample']) for r in summary['runs']} ==
                {('shared', 1), ('shared', 2), ('separate', 1), ('separate', 2)},
                'Unexpected campaign cases.')
        for run in summary['runs']:
            payload = campaign.read(f"{run['case']}/live-{run['sample']}.zip")
            require(hashlib.sha256(payload).hexdigest() == run['sha256'],
                    'Nested live archive SHA mismatch.')
            with zipfile.ZipFile(io.BytesIO(payload)) as live:
                require(live.testzip() is None, 'Live ZIP CRC failure.')
                result = json.loads(live.read('run-acceptance.json'))
                plan = json.loads(live.read('relationship_scenario_plan.json'))
                receipt = result['runtime_receipt']
                require(result['native_exit'] == 0, 'Native run did not complete.')
                require(receipt['status'] == 'LIVE_CALLBACKS_COMPLETE', 'Incomplete receipt.')
                namespace = receipt['identity_program']['namespace']
                require(namespace not in namespaces, 'Repeated resource namespace.')
                namespaces.add(namespace)
                observations = receipt['identity_program']['observations']
                expected_count = 46 if run['case'] == 'shared' else 57
                require(len(observations) == expected_count, 'Unexpected response count.')
                total += len(observations)
                issues = []
                try:
                    validate_identity_receipts(receipt, plan)
                except IdentityMismatch as exc:
                    issues = ast.literal_eval(str(exc))
                expected_issues = [] if run['case'] == 'shared' else [
                    {'step': 'foreign_add_a', 'kind': 'HTTP_POLICY_MISMATCH',
                     'expected': [403, 404], 'observed': 500},
                    {'step': 'foreign_add_b', 'kind': 'HTTP_POLICY_MISMATCH',
                     'expected': [403, 404], 'observed': 500}]
                require(issues == expected_issues, 'Unexpected qualification issues.')
                if run['case'] == 'separate':
                    for actor in ('a', 'b'):
                        probe = observations['foreign_add_' + actor]
                        require(probe['body'] == 'Internal Server Error', 'Unexpected 500 body.')
                        require(probe['request_body'] == {'recipeIncrementQuantity': 1},
                                'Unexpected foreign-add request body.')
                        require(observations['add_' + actor]['code'] == 200,
                                'Own recipe control failed.')
                recorded = next(r for r in qualified['runs']
                                if r['case'] == run['case'] and r['sample'] == run['sample'])
                require(recorded['independent_issues'] == issues, 'Report issues differ.')
                require(recorded['live_sha256'] == run['sha256'], 'Report hash differs.')
    require(total == 206, 'Campaign response total differs.')
    return total


if __name__ == '__main__':
    count = verify(Path(__file__).resolve().parent)
    print(f'MULTI_IDENTITY_EVIDENCE_VERIFIED: four complete runs; {count} responses; four HTTP 500 manifestations; one candidate defect. No API requests sent.')
