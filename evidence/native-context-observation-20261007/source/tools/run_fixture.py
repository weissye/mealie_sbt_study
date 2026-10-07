"""Generate native Context projects and run only against an isolated loopback fixture."""
import argparse
import json
import shutil
import subprocess
import sys
import threading
import zipfile
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from generator_v56.render.context_observation import generate


class Fixture(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def body(self):
        data = self.rfile.read(int(self.headers.get('Content-Length', '0')))
        return json.loads(data or b'{}')

    def reply(self, status, body):
        payload = body.encode() if isinstance(body, str) else json.dumps(body).encode()
        self.server.receipts.append({'method': self.command, 'path': self.path, 'status': status})
        self.send_response(status)
        self.send_header('Content-Type', 'text/plain' if isinstance(body, str) else 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        body = self.body()
        if self.path == '/resources':
            self.server.resource = {'id': 'fixture-1', 'name': body['name']}
            self.reply(201, self.server.resource)
        elif self.path == '/resources/fixture-1/action':
            if self.server.mode == 'control':
                self.reply(200, self.server.resource)
            else:
                if self.server.mode == 'changed':
                    self.server.resource['name'] = 'injected-change'
                self.reply(500, 'Internal Server Error')
        else:
            self.reply(404, {})

    def do_PATCH(self):
        body = self.body()
        if self.path == '/resources/fixture-1' and self.server.resource:
            self.server.resource.update(body)
            self.reply(200, self.server.resource)
        else:
            self.reply(404, {})

    def do_GET(self):
        if self.path == '/resources/fixture-1' and self.server.resource:
            self.reply(200, self.server.resource)
        else:
            self.reply(404, {})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--generate-only', action='store_true')
    args = parser.parse_args()
    runner = shutil.which('provengo') or shutil.which('provengo.bat')
    if not args.generate_only and not runner:
        raise SystemExit('Provengo not found on PATH')
    root = args.root / ('runs/context-observation-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    root.mkdir(parents=True)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Fixture)
    server.receipts = []
    server.resource = None
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    results = []
    try:
        if not args.generate_only:
            version = subprocess.run([runner, '--version'], capture_output=True, text=True, errors='replace', timeout=30)
            (root / 'provengo-version.txt').write_text(version.stdout + version.stderr, encoding='utf-8')
        for mode in ['control', 'error', 'changed']:
            server.mode = mode
            server.resource = None
            server.receipts = []
            project = root / mode
            generate(args.root / 'model/fixture-openapi.json', project / 'spec/js',
                     'http://127.0.0.1:' + str(server.server_port))
            if args.generate_only:
                continue
            try:
                process = subprocess.run([runner, 'run', str(project.resolve())], capture_output=True,
                                         text=True, errors='replace', timeout=180)
                log = process.stdout + '\n' + process.stderr
                code = process.returncode
            except subprocess.TimeoutExpired:
                log = 'PROBE_TIMEOUT'
                code = None
            (project / 'native-run.log').write_text(log, encoding='utf-8')
            evidence = []
            for line in log.splitlines():
                marker = 'CONTEXT_OBSERVATION_EVIDENCE '
                if marker in line:
                    evidence.append(json.loads(line.split(marker, 1)[1]))
            expected_requests = [('POST', '/resources', 201), ('GET', '/resources/fixture-1', 200),
                                 ('PATCH', '/resources/fixture-1', 200), ('GET', '/resources/fixture-1', 200),
                                 ('POST', '/resources/fixture-1/action', 200 if mode == 'control' else 500),
                                 ('GET', '/resources/fixture-1', 200)]
            observed_requests = [(r['method'], r['path'], r['status']) for r in server.receipts]
            e = evidence[0] if len(evidence) == 1 else {}
            accepted = bool(observed_requests == expected_requests and e.get('observationsComplete')
                            and e.get('identityMatches') and e.get('revision') == 2
                            and e.get('contextExpected') == {'name': 'updated'}
                            and e.get('baseline') == {'id': 'fixture-1', 'name': 'updated'}
                            and e.get('baselineMatches') == (mode != 'changed')
                            and e.get('expectedMatches') == (mode != 'changed')
                            and e.get('contractStatusValid') == (mode == 'control')
                            and 'CONTEXT_REVISION_VERIFIED revision=1' in log
                            and 'CONTEXT_REVISION_VERIFIED revision=2' in log
                            and (any('Test Result: ' + status in log for status in ('SUCCESS', 'PASS')) if mode == 'control' else 'Test Result: FAIL' in log)
                            and (code == 0 if mode == 'control' else code not in (None, 0)))
            results.append({'case': mode, 'accepted': accepted, 'exit_code': code,
                            'fixture_requests': server.receipts[:], 'evidence': evidence})
            print('CASE ' + mode + ': ' + ('ACCEPTED' if accepted else 'NOT_ACCEPTED'))
            if not accepted:
                break
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
    accepted = len(results) == 3 and all(r['accepted'] for r in results)
    summary = {'status': 'GENERATED_NOT_EXECUTED' if args.generate_only else
               'NATIVE_CONTEXT_OBSERVATION_ACCEPTANCE_PASS' if accepted else 'NATIVE_CONTEXT_OBSERVATION_NOT_ACCEPTED',
               'sut_requests': 0, 'fixture_only': True, 'native_provengo_executed': bool(results), 'cases': results}
    (root / 'result.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    with zipfile.ZipFile(root / 'review.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob('*')):
            if p.is_file() and p.name != 'review.zip':
                z.write(p, str(p.relative_to(root)))
    print(summary['status'])
    print('Review ZIP:', root / 'review.zip')
    if not args.generate_only and not accepted:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
