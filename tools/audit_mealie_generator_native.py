"""Offline native sampling of the installed generator. Never performs replay."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

def digest(data):
    return hashlib.sha256(data).hexdigest()

def audit_events(samples, expected_workers):
    if not isinstance(samples, list) or len(samples) != 1 or not isinstance(samples[0], list):
        raise ValueError('Expected exactly one native sample array')
    pending = set()
    finishes = {}
    steps = {}
    errors = []
    verified = 0
    for event in samples[0]:
        data = event.get('data') or {}
        name = event.get('name')
        owner = data.get('owner')
        if name == 'SBT:CrudStep':
            key = (owner, data.get('stage'))
            if key in pending:
                errors.append('Duplicate outstanding step: ' + str(key))
            pending.add(key)
            steps[key[1]] = steps.get(key[1], 0) + 1
        elif name == 'SBT:CrudVerified':
            key = (owner, data.get('stage'))
            if key not in pending:
                errors.append('Unmatched verifier event: ' + str(key))
            else:
                pending.remove(key)
            verified += 1
        elif name == 'SBT:WorkerFinished':
            if owner in finishes:
                errors.append('Duplicate worker completion: ' + str(owner))
            finishes[owner] = data.get('reason')
    missing = sorted(set(expected_workers) - set(finishes))
    unsuccessful = {k: v for k, v in finishes.items() if v != 'complete'}
    complete = not errors and not missing and not unsuccessful and not pending and bool(expected_workers)
    return {'status': 'NATIVE_SYMBOLIC_WORKERS_COMPLETE' if complete else 'NATIVE_SYMBOLIC_INCOMPLETE',
            'event_count': len(samples[0]), 'expected_workers': len(expected_workers),
            'finished_workers': len(finishes), 'missing_workers': missing,
            'unsuccessful_workers': unsuccessful, 'pending_verifications': [list(p) for p in sorted(pending)],
            'steps': steps, 'symbolic_verifier_events': verified, 'errors': errors,
            'runtime_verifiers_evaluated': False, 'bugs_reproduced': 0}

def native_command(jar, project, output, max_events):
    return ['java', '-Xmx1g', '-jar', str(jar), 'sample', '--algorithm', 'random',
            '--size', '1', '--max-length', str(max_events), '-o', str(output), str(project)]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--jar', type=Path)
    parser.add_argument('--max-events', type=int, default=600)
    parser.add_argument('--timeout', type=int, default=90)
    parser.add_argument('--contract', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    source = root / 'generic-generator/generator_v56'
    contract = (args.contract or root / 'generic-generator/compatibility/contracts/mealie.json').resolve()
    pins = json.loads(Path(__file__).with_name('mealie_native_acceptance_pins.json').read_text())
    if not 100 <= args.max_events <= 3000 or not 15 <= args.timeout <= 300:
        raise ValueError('Invalid sampling bounds')
    # Accept CRLF checkout without modifying original bytes. Both hashes recorded.
    raw = contract.read_bytes()
    if digest(raw.replace(b'\r\n', b'\n')) != pins['contract_normalized_sha256']:
        raise ValueError('Contract differs beyond line endings; generation stopped')
    for name, expected in pins['critical_source_normalized_sha256'].items():
        if digest((source / name).read_bytes().replace(b'\r\n', b'\n')) != expected:
            raise ValueError('Installed critical source differs: ' + name)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    run = root / 'runs' / ('generator-native-acceptance-' + stamp)
    run.mkdir(parents=True)
    report = {'status': 'PREPARING', 'server_requests': 0, 'live_replay_executed': False,
              'resource_mutations': 0, 'five_findings_reproduced': False,
              'contract_raw_sha256': digest(raw), 'contract_normalized_sha256': digest(raw.replace(b'\r\n', b'\n')),
              'source_sha256': {str(p.relative_to(source)): digest(p.read_bytes()) for p in sorted(source.rglob('*.py'))},
              'external_semantic_profiles_supplied': False,
              'scope': 'Native symbolic architecture acceptance, not live bug reproduction'}
    try:
        sys.path.insert(0, str(source.parent))
        from generator_v56 import __version__
        from generator_v56.pipeline import run_pipeline
        report['generator_version'] = __version__
        if __version__ != pins['generator_version']:
            raise ValueError('Generator version differs')
        result = run_pipeline(str(contract), 'mealie', 'http://127.0.0.1:9925', 203,
                              story_profile='parallel-crud', instances_per_entity=2,
                              logical_processes=1, include_resource_maps=True)
        project = run / 'model'
        js = project / 'spec/js'
        js.mkdir(parents=True)
        (project / 'config').mkdir()
        (project / 'config/provengo.yml').write_text('version: 2\n')
        (js / 'interfaces.mealie.js').write_text(result.interfaces_js, encoding='utf-8', newline='\n')
        (js / 'stories.mealie.js').write_text(result.stories_js, encoding='utf-8', newline='\n')
        report['architecture'] = {
            'direct_http_in_stories': bool(re.search(r'\bsvc\.(get|post|put|patch|delete)\s*\(', result.stories_js)),
            'business_bridge_present': '/sbt/step/' in result.interfaces_js + result.stories_js,
            'bthreads': result.stories_js.count('bthread('),
            'semantic_runtime_correctness_proven': False}
        if report['architecture']['direct_http_in_stories'] or report['architecture']['business_bridge_present']:
            raise ValueError('Architecture boundary rejected')
        for name, data in [('generation_report.json', result.generation_report), ('resource_maps.json', result.resource_maps)]:
            (run / name).write_text(json.dumps(data, indent=2), encoding='utf-8')
        workers = re.findall(r'bthread\("crud:([^"\n]+)"', result.stories_js)
        samples = run / 'samples.json'
        if args.jar:
            if not args.jar.is_file():
                raise ValueError('Provengo JAR does not exist')
            command = native_command(args.jar.resolve(), project, samples, args.max_events)
            report['provengo_jar_sha256'] = digest(args.jar.read_bytes())
        else:
            executable = shutil.which('provengo')
            if not executable:
                raise ValueError('Provengo missing on PATH; supply --jar')
            command = [executable, 'sample', '--algorithm', 'random', '--size', '1',
                       '--max-length', str(args.max_events), '-o', str(samples), str(project)]
            if os.name == 'nt' and executable.lower().endswith(('.bat', '.cmd')):
                if any(any(c in x for c in ('"', '\r', '\n', '%', '\0')) for x in command):
                    raise ValueError('Unsupported batch argument')
                command = subprocess.list2cmdline([os.environ.get('COMSPEC', 'cmd.exe')]) + ' /d /s /v:off /c "' + ' '.join('"' + x + '"' for x in command) + '"'
        print('Native symbolic sampling. No Mealie requests sent.', flush=True)
        try:
            response = subprocess.run(command, capture_output=True, text=True, encoding='utf-8',
                                      errors='replace', timeout=args.timeout)
            (run / 'sample-output.txt').write_text(response.stdout + '\n' + response.stderr, encoding='utf-8')
            report['sample_exit_code'] = response.returncode
        except subprocess.TimeoutExpired as error:
            out = error.stdout or b''
            err = error.stderr or b''
            (run / 'sample-output.txt').write_bytes((out.encode() if isinstance(out, str) else out) + (err.encode() if isinstance(err, str) else err))
            raise ValueError('Native sampling timed out; partial evidence preserved')
        if response.returncode != 0 or not samples.exists():
            raise ValueError('Native sample absent or sampler failed; inspect sample-output.txt')
        report['samples_bytes'] = samples.stat().st_size
        if samples.stat().st_size > 16 * 1024 * 1024:
            raise ValueError('Sample exceeds 16 MiB audit memory bound; evidence retained')
        report['sample_audit'] = audit_events(json.loads(samples.read_text()), workers)
        report['status'] = report['sample_audit']['status']
    except Exception as error:
        report['status'] = 'NATIVE_ACCEPTANCE_NOT_COMPLETE'
        report['error'] = str(error)
    finally:
        (run / 'acceptance-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        with zipfile.ZipFile(run / 'review.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(run.rglob('*')):
                if path.is_file() and path.name != 'review.zip':
                    archive.write(path, path.relative_to(run).as_posix())
        print(report['status'])
        print('Review ZIP:', run / 'review.zip')
        print('Live reproduction remains pending for all five findings.')
    return 0 if report['status'] == 'NATIVE_SYMBOLIC_WORKERS_COMPLETE' else 2

if __name__ == '__main__':
    sys.exit(main())
