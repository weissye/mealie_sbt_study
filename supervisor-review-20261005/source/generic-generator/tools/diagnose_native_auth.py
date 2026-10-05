"""Compare direct and native authentication through an ephemeral local relay."""
import argparse
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import threading
import urllib.parse
import uuid
import zipfile

from relationship_execution import native, redact


def inspect_form(body, content_types, username, password):
    try:
        text = body.decode('utf-8')
        fields = urllib.parse.parse_qs(text, keep_blank_values=True)
        json_string = isinstance(json.loads(text), str) if text.startswith('"') else False
    except (UnicodeError, ValueError):
        fields = {}
        json_string = False
    return {'content_types': content_types, 'body_is_json_string': json_string,
            'username_matches_input': fields.get('username') == [username],
            'password_matches_input': fields.get('password') == [password],
            'grant_type_is_password': fields.get('grant_type') == ['password'],
            'duplicate_username': len(fields.get('username', [])) > 1,
            'duplicate_password': len(fields.get('password', [])) > 1}


def forward(base, path, body, headers):
    parsed = urllib.parse.urlsplit(base)
    if parsed.scheme != 'http' or parsed.hostname not in ('127.0.0.1', 'localhost') or parsed.path not in ('', '/'):
        raise ValueError('This diagnostic requires a local HTTP origin.')
    connection = http.client.HTTPConnection(parsed.hostname, parsed.port or 80, timeout=20)
    try:
        connection.putrequest('POST', path, skip_host=True, skip_accept_encoding=True)
        connection.putheader('Host', parsed.netloc)
        for name, value in headers:
            if name.lower() not in ('host', 'content-length', 'connection', 'transfer-encoding'):
                connection.putheader(name, value)
        connection.putheader('Content-Length', str(len(body)))
        connection.endheaders(body)
        response = connection.getresponse()
        result = response.read(1024 * 1024 + 1)
        if len(result) > 1024 * 1024:
            raise ValueError('Authentication response exceeds diagnostic limit.')
        return response.status, response.getheader('Content-Type', 'application/json'), result
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--openapi', required=True, type=Path)
    parser.add_argument('--base-url', default='http://127.0.0.1:9925')
    parser.add_argument('--review-zip', required=True, type=Path)
    args = parser.parse_args()
    username, password = os.environ.get('SBT_REL_USERNAME'), os.environ.get('SBT_REL_PASSWORD')
    if not username or not password:
        raise ValueError('Credentials must be supplied by the PowerShell wrapper.')
    spec = json.loads(args.openapi.read_text(encoding='utf-8-sig'))
    paths = {scheme['flows']['password']['tokenUrl'] for scheme in spec.get('components', {}).get('securitySchemes', {}).values() if scheme.get('flows', {}).get('password')}
    if len(paths) != 1:
        raise ValueError('One documented password token endpoint is required.')
    path = paths.pop()
    if not path.startswith('/') or path.startswith('//') or '?' in path:
        raise ValueError('The token endpoint must be a local relative path.')
    project = args.root / 'provengo' / ('auth-diagnostic-' + uuid.uuid4().hex[:12])
    js = project / 'spec/js'
    js.mkdir(parents=True)
    (project / 'config').mkdir()
    (project / 'config/provengo.yml').write_text('version: 2\n')
    result = {'status': 'AUTH_DIAGNOSTIC_NOT_ACCEPTED', 'resource_mutations': 0, 'automatic_retry': False}
    observed = []

    class Relay(BaseHTTPRequestHandler):
        def log_message(self, *unused):
            pass

        def do_POST(self):
            if self.path != path or observed:
                self.send_error(403)
                return
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 65536 or self.headers.get('Transfer-Encoding'):
                self.send_error(400)
                return
            body = self.rfile.read(size)
            inspection = inspect_form(body, self.headers.get_all('Content-Type') or [], username, password)
            observed.append(inspection)
            try:
                status, content_type, response_body = forward(args.base_url, path, body, list(self.headers.raw_items()))
                inspection['forwarded_http_status'] = status
                self.send_response(status)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(response_body)))
                self.end_headers()
                self.wfile.write(response_body)
            except Exception as error:
                inspection['relay_error_type'] = type(error).__name__
                self.send_error(502)

    relay = ThreadingHTTPServer(('127.0.0.1', 0), Relay)
    relay.daemon_threads = True
    thread = threading.Thread(target=relay.serve_forever, daemon=True)
    thread.start()
    logs = []
    try:
        direct_body = urllib.parse.urlencode({'username': username, 'password': password, 'remember_me': 'false'}).encode()
        direct_status, _, direct_response = forward(args.base_url, path, direct_body, [('Content-Type', 'application/x-www-form-urlencoded')])
        result['direct_http_status'] = direct_status
        try:
            result['direct_token_present'] = bool(json.loads(direct_response).get('access_token'))
        except ValueError:
            result['direct_token_present'] = False
        del direct_response
        if direct_status != 200 or not result['direct_token_present']:
            result['status'] = 'DIRECT_AUTH_NOT_ACCEPTED'
        else:
            base = 'http://127.0.0.1:' + str(relay.server_port)
            options = '''{headers:{"Content-Type":"application/x-www-form-urlencoded"},body:"grant_type=password&username=@{encodeURIComponent(getEnv('SBT_REL_USERNAME'))}&password=@{encodeURIComponent(getEnv('SBT_REL_PASSWORD'))}",expectedResponseCodes:[200],callback:function(response){var value=JSON.parse(response.body);if(!value.access_token){pvg.fail("Authentication token missing");return;}pvg.success("SBT_AUTH_DIAGNOSTIC_TOKEN_PRESENT");}}'''
            interfaces = '// @provengo summon rest\n// @provengo summon rtv\n// @provengo summon context\nvar diagSvc=new RESTSession(' + json.dumps(base) + ',"auth-diagnostic",{});\nfunction diagnosticLogin(){diagSvc.post(' + json.dumps(path) + ',' + options + ');}\n'
            (js / 'interfaces.auth.js').write_text(interfaces, encoding='utf-8')
            (js / 'stories.auth.js').write_text('bthread("auth-only",function(){diagnosticLogin();});\n', encoding='utf-8')
            samples = project / 'auth-sample.json'
            sampled = native(['sample', '--algorithm', 'random', '--size', '1', '--max-length', '10', '-o', str(samples)], project)
            logs.append(sampled.stdout + '\n' + sampled.stderr)
            result['native_sample_exit_code'] = sampled.returncode
            if sampled.returncode:
                result['status'] = 'AUTH_DIAGNOSTIC_SAMPLING_FAILED'
            else:
                run = native(['--batch-mode', 'run', '--run-source', str(samples), '--run-id', '1'], project)
                logs.append(run.stdout + '\n' + run.stderr)
                result['native_run_exit_code'] = run.returncode
                result['native_wire_requests'] = observed
                result['status'] = 'AUTH_DIAGNOSTIC_WIRE_CAPTURED' if observed else 'AUTH_DIAGNOSTIC_NO_WIRE_REQUEST'
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        result['error'] = redact(str(error))
    finally:
        relay.shutdown()
        relay.server_close()
        thread.join(timeout=2)
        result['native_wire_requests'] = observed
        report = project / 'auth-diagnostic.json'
        report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        log = project / 'auth-diagnostic-output.txt'
        log.write_text(redact('\n'.join(logs)), encoding='utf-8')
        args.review_zip.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.review_zip, 'w', zipfile.ZIP_DEFLATED) as archive:
            for item in [report, log] + list(js.glob('*.js')):
                archive.write(item, item.relative_to(project))
    print(json.dumps(result, indent=2))
    print('Review ZIP: ' + str(args.review_zip))
    print('Authentication requests only. No resource creation, deletion, or replay was performed.')
    return 0 if observed else 1


if __name__ == '__main__':
    raise SystemExit(main())
