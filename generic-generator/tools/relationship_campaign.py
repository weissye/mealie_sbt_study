"""Aggregate small native reviews without replaying or contacting any server."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

if __package__:
    from .relationship_execution import bundle, model_hashes, redact, validate_negative_receipts, write
else:
    from relationship_execution import bundle, model_hashes, redact, validate_negative_receipts, write


def evaluate_project(project):
    project = Path(project)
    plan = json.loads((project / 'relationship_scenario_plan.json').read_text(encoding='utf-8-sig'))
    compilation = json.loads((project / 'relationship_compilation.json').read_text(encoding='utf-8-sig'))
    sample = json.loads((project / 'execution-review/sample-acceptance.json').read_text(encoding='utf-8-sig'))
    live = json.loads((project / 'execution-review/run-acceptance.json').read_text(encoding='utf-8-sig'))
    if sample.get('status') != 'NATIVE_SYMBOLIC_SAMPLES_COMPLETE' or sample.get('model_sha256') != model_hashes(project):
        raise ValueError('Sampling evidence does not match the current generated model.')
    orders = sample.get('task_orders', [])
    sample_id = live.get('sample_id', 0)
    if type(sample_id) is not int or not 1 <= sample_id <= len(orders):
        raise ValueError('Live evidence does not identify an audited sample.')
    tasks = {task['id']: task for task in plan['tasks']}
    done = set()
    order = orders[sample_id - 1]
    for task_id in order:
        if task_id not in tasks or task_id in done or not set(tasks[task_id]['after']).issubset(done):
            raise ValueError('Recorded task order violates the generated plan.')
        done.add(task_id)
    if done != set(tasks):
        raise ValueError('Recorded task order is incomplete.')
    if live.get('status') != 'NATIVE_RELATIONSHIP_CALLBACKS_PASS' or live.get('native_exit_code') != 0 or live.get('live_accepted') is not True:
        raise ValueError('Native live execution was not accepted: ' + str(live.get('error', live.get('status'))))
    receipt = live.get('runtime_receipt', {})
    if receipt.get('status') != 'LIVE_CALLBACKS_COMPLETE' or receipt.get('task_count') != len(tasks) or receipt.get('response_count') != compilation['http_requests_per_complete_schedule'] or receipt.get('owned_instances') != sum(map(len, plan['instances'].values())):
        raise ValueError('Native runtime receipt is incomplete.')
    validate_negative_receipts(receipt, plan)
    # This extended campaign deliberately requires full member evidence.
    probes = [task for task in tasks.values() if task['kind'] == 'negative_link']
    if not probes or not all(task.get('verify_cycle_members') for task in probes):
        raise ValueError('Expanded campaign requires complete cycle member verification.')
    return {'project': str(project), 'status': 'NATIVE_RELATIONSHIP_CALLBACKS_PASS',
            'task_order_sha256': hashlib.sha256(json.dumps(order, separators=(',', ':')).encode()).hexdigest(),
            'task_order': order, 'task_count': len(tasks), 'response_count': receipt['response_count'],
            'owned_instances': receipt['owned_instances'], 'negative_tests': receipt['negative_tests'],
            'model_sha256': sample['model_sha256'], 'reset_replay_accepted': False}


def summarize(projects, expected_runs):
    runs = []
    visited = set()
    for project in projects:
        try:
            resolved = str(Path(project).resolve())
            if resolved in visited:
                raise ValueError('Duplicate project cannot count as an independent campaign run.')
            visited.add(resolved)
            runs.append(evaluate_project(project))
        except (ValueError, OSError, KeyError, TypeError) as error:
            runs.append({'project': str(project), 'status': 'NOT_ACCEPTED', 'error': redact(str(error))})
    passed = [run for run in runs if run['status'] == 'NATIVE_RELATIONSHIP_CALLBACKS_PASS']
    distinct = len({run['task_order_sha256'] for run in passed})
    complete = len(runs) == expected_runs and len(passed) == expected_runs
    status = 'EXPANDED_CAMPAIGN_NOT_ACCEPTED'
    if complete:
        status = ('EXPANDED_SINGLE_RUN_PASS' if expected_runs == 1 else
                  'EXPANDED_CAMPAIGN_PASS' if distinct > 1 else 'EXPANDED_CAMPAIGN_NO_SCHEDULE_VARIATION')
    return {'status': status, 'expected_runs': expected_runs, 'recorded_runs': len(runs),
            'accepted_runs': len(passed), 'distinct_task_orders': distinct,
            'schedule_variation_observed': distinct > 1, 'runs': runs,
            'live_server_requests_sent_by_collector': 0, 'automatic_retry': False,
            'automatic_deletion': False, 'reset_replay_accepted': False,
            'coverage_limit': 'Bounded generated schedules and cycle member snapshots; no general bug-freedom claim.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--review-zip', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8-sig'))
    projects = [Path(value) for value in manifest['projects']]
    report = summarize(projects, manifest['expected_runs'])
    report_path = args.manifest.parent / 'campaign-acceptance.json'
    write(report_path, redact(report))
    args.review_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.review_zip, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.write(report_path, report_path.name)
        archive.write(args.manifest, 'campaign-manifest.json')
        for index, project in enumerate(projects, 1):
            if not project.exists():
                continue
            small_review = args.manifest.parent / ('run-' + str(index) + '-review.zip')
            bundle(project, list((project / 'execution-review').glob('*')), small_review)
            archive.write(small_review, small_review.name)
    print(report['status'])
    print('Accepted runs: ' + str(report['accepted_runs']))
    print('Distinct task orders: ' + str(report['distinct_task_orders']))
    print('Review ZIP: ' + str(args.review_zip))
    return 0 if report['status'] in {'EXPANDED_SINGLE_RUN_PASS', 'EXPANDED_CAMPAIGN_PASS'} else 1


if __name__ == '__main__':
    sys.exit(main())
