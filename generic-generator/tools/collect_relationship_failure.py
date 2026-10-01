"""Collect bounded, redacted evidence from an existing failed native run.

No API requests or resource mutations are performed. Docker is used only for
the logs subcommand, with a bounded time window and timeout.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

from relationship_execution import redact


def compact_failures(value):
    records = []

    def visit(node, path):
        if len(records) >= 80:
            return
        if isinstance(node, dict):
            for key, item in node.items():
                lowered = key.lower()
                if lowered in ('error', 'errors', 'failure', 'failures', 'exception', 'message', 'messages', 'detail', 'reason'):
                    records.append({'path': path + '/' + key, 'value': redact(json.dumps(item, ensure_ascii=False))[:6000]})
                elif lowered in ('code', 'statuscode', 'httpstatus', 'responsecode') and str(item).isdigit() and 400 <= int(item) < 600:
                    records.append({'path': path, 'status': item,
                                    'response_fields': {k: redact(v) for k, v in node.items() if k.lower() in ('body', 'responsebody', 'detail', 'message') and isinstance(v, (str, int))}})
                visit(item, path + '/' + key)
        elif isinstance(node, list):
            for index, item in enumerate(node):
                visit(item, path + '/' + str(index))
        elif isinstance(node, str) and re.search(r'circular|cyclic|recursion|unexpected response|\bFAIL\b|\bERROR\b', node, re.I):
            records.append({'path': path, 'value': redact(node)[:6000]})

    visit(value, '')
    return records


def collect(project, destination, container, since, until):
    project = Path(project).resolve()
    if not (project / 'relationship_scenario_plan.json').is_file():
        raise ValueError('Project does not contain a generated relationship plan.')
    destination = Path(destination).resolve()
    if destination.is_relative_to(project):
        raise ValueError('Review ZIP must be outside the generated project.')
    report = {'status': 'READ_ONLY_FAILURE_EVIDENCE_COLLECTED', 'api_requests': 0,
              'resource_mutations': 0, 'live_accepted': False, 'source_files': [],
              'container': container, 'since': since, 'until': until}
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        names = ['relationship_scenario_plan.json', 'relationship_compilation.json',
                 'readiness.json', 'execution-review/run-acceptance.json',
                 'execution-review/run-output.txt']
        for name in names:
            source = project / name
            if not source.is_file():
                continue
            if source.stat().st_size > 8 * 1024 * 1024:
                report['source_files'].append({'path': name, 'status': 'SKIPPED_SIZE_LIMIT'})
                continue
            data = source.read_bytes()
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(redact(data.decode('utf-8-sig')), encoding='utf-8')
            report['source_files'].append({'path': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
        native = project / 'execution-review/native-result.json'
        if native.is_file() and native.stat().st_size <= 32 * 1024 * 1024:
            try:
                findings = compact_failures(json.loads(native.read_text(encoding='utf-8-sig')))
                (root / 'native-failure-extract.json').write_text(json.dumps(findings, indent=2), encoding='utf-8')
                report['native_result'] = {'status': 'COMPACT_FIELDS_EXTRACTED', 'findings': len(findings), 'bytes': native.stat().st_size}
            except (ValueError, UnicodeError) as error:
                report['native_result'] = {'status': 'INVALID_JSON', 'error': str(error)}
        else:
            report['native_result'] = {'status': 'MISSING' if not native.is_file() else 'SKIPPED_SIZE_LIMIT',
                                       'bytes': native.stat().st_size if native.is_file() else 0}
        executable = shutil.which('docker')
        if not executable:
            report['docker_logs'] = {'status': 'DOCKER_CLIENT_UNAVAILABLE'}
        else:
            try:
                output = root / 'server-log.raw'
                with output.open('wb') as stream:
                    result = subprocess.run([executable, 'logs', '--timestamps', '--tail', '1000', '--since', since,
                                             '--until', until, container], stdout=stream, stderr=subprocess.STDOUT, timeout=30)
                with output.open('rb') as stream:
                    raw = stream.read(4 * 1024 * 1024)
                (root / 'server-log.txt').write_text(redact(raw.decode('utf-8', errors='replace')), encoding='utf-8')
                output.unlink()
                report['docker_logs'] = {'status': 'CAPTURED' if result.returncode == 0 else 'DOCKER_LOGS_ERROR',
                                         'exit_code': result.returncode, 'captured_bytes': len(raw)}
            except subprocess.TimeoutExpired:
                (root / 'server-log.raw').unlink(missing_ok=True)
                report['docker_logs'] = {'status': 'TIMEOUT'}
            except OSError as error:
                (root / 'server-log.raw').unlink(missing_ok=True)
                report['docker_logs'] = {'status': 'UNAVAILABLE', 'error': str(error)}
        (root / 'collection-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        destination.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
            for source in sorted(root.rglob('*')):
                if source.is_file():
                    archive.write(source, str(source.relative_to(root)))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--container', default='mealie-sbt-study-mealie-1')
    parser.add_argument('--since', required=True)
    parser.add_argument('--until', required=True)
    args = parser.parse_args()
    report = collect(args.project, args.output, args.container, args.since, args.until)
    print(report['status'])
    print('Review ZIP: ' + str(Path(args.output).resolve()))
    print('No API requests, retries, resource creation, deletion or reset were performed.')
    print('Docker logs status: ' + report['docker_logs']['status'])


if __name__ == '__main__':
    main()
