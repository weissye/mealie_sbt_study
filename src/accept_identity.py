"""Local identity acceptance: one token request and three authenticated reads."""
import argparse
import getpass
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from rtv import RTV

PINNED_HASH = '90e19aa713ab4ba15352627aca7dc37290f868b213eb65a3e1564f3b7a7ff292'
READ_PATHS = ('/api/users/self', '/api/groups/self', '/api/households/self')

class AcceptanceError(ValueError):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

class LocalClient:
    def __init__(self, base_url):
        parsed = urllib.parse.urlsplit(base_url)
        if (parsed.scheme != 'http' or parsed.hostname != '127.0.0.1' or
                parsed.username or parsed.password or parsed.query or parsed.fragment or
                parsed.path not in ('', '/') or not parsed.port):
            raise AcceptanceError('Only an explicit http://127.0.0.1:<port> endpoint is supported.')
        self.base = base_url.rstrip('/')
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def request(self, path, token=None, credentials=None):
        if path not in READ_PATHS + ('/api/auth/token',):
            raise AcceptanceError('Operation is outside identity acceptance.')
        data = None
        headers = {'Accept': 'application/json'}
        if credentials is not None:
            if path != '/api/auth/token':
                raise AcceptanceError('Credentials are only permitted on the token endpoint.')
            data = urllib.parse.urlencode(credentials).encode('utf-8')
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        elif path == '/api/auth/token':
            raise AcceptanceError('The token endpoint requires credentials.')
        if token:
            headers['Authorization'] = 'Bearer ' + token
        request = urllib.request.Request(self.base + path, data=data, headers=headers)
        try:
            with self.opener.open(request, timeout=15) as response:
                status = response.status
                body = response.read(2 * 1024 * 1024 + 1)
        except urllib.error.HTTPError as error:
            raise AcceptanceError('HTTP ' + str(error.code) + ' from ' + path) from None
        except (urllib.error.URLError, OSError):
            raise AcceptanceError('Local server connection failed for ' + path) from None
        if status != 200 or len(body) > 2 * 1024 * 1024:
            raise AcceptanceError('Unexpected status or response size from ' + path)
        try:
            value = json.loads(body)
        except (ValueError, UnicodeError):
            raise AcceptanceError('Invalid JSON from ' + path) from None
        if not isinstance(value, dict):
            raise AcceptanceError('Expected an object from ' + path)
        return status, value

def identity_uuid(value, label):
    if not isinstance(value, str):
        raise AcceptanceError('Missing UUID identity: ' + label)
    try:
        return str(uuid.UUID(value))
    except ValueError:
        raise AcceptanceError('Invalid UUID identity: ' + label) from None

def accepted_observations(client, username, password, run_id):
    statuses = []
    status, auth = client.request('/api/auth/token', credentials={
        'username': username, 'password': password, 'remember_me': 'false'})
    if status != 200:
        raise AcceptanceError('Authentication did not return HTTP 200.')
    token = auth.get('access_token')
    if not isinstance(token, str) or not token:
        raise AcceptanceError('The authentication response did not contain an access token.')
    if str(auth.get('token_type', 'bearer')).lower() != 'bearer':
        raise AcceptanceError('Unsupported token type.')
    statuses.append({'method': 'POST', 'path': '/api/auth/token', 'status': status})
    bodies = []
    for path in READ_PATHS:
        status, body = client.request(path, token=token)
        if status != 200:
            raise AcceptanceError('Identity read did not return HTTP 200 from ' + path)
        statuses.append({'method': 'GET', 'path': path, 'status': status})
        bodies.append(body)
    user, group, household = bodies
    user_id = identity_uuid(user.get('id'), 'User.id')
    group_id = identity_uuid(group.get('id'), 'Group.id')
    household_id = identity_uuid(household.get('id'), 'Household.id')
    if (identity_uuid(user.get('groupId'), 'User.groupId') != group_id or
            identity_uuid(household.get('groupId'), 'Household.groupId') != group_id or
            identity_uuid(user.get('householdId'), 'User.householdId') != household_id):
        raise AcceptanceError('Observed user, group and household IDs do not agree.')
    for field, owner in (('groupSlug', group), ('householdSlug', household)):
        if not isinstance(owner.get('slug'), str) or not owner['slug'] or user.get(field) != owner['slug']:
            raise AcceptanceError('Observed scope slugs do not agree: ' + field)
    scope = {'group': group_id, 'household': household_id}
    rtv = RTV(run_id)
    group_record = rtv.observe('Group', 'G1', {'group': group_id},
        {'id': group_id, 'slug': group['slug']}, 'GET /api/groups/self')
    household_record = rtv.observe('Household', 'H1', scope,
        {'id': household_id, 'slug': household['slug']}, 'GET /api/households/self',
        values={'groupId': group_id})
    user_identifiers = {'id': user_id}
    if isinstance(user.get('username'), str) and user['username']:
        user_identifiers['username'] = user['username']
    user_record = rtv.observe('User', 'U1', scope, user_identifiers, 'GET /api/users/self',
        values={'groupId': group_id, 'householdId': household_id})
    rtv.observe_link('Household.groupId', household_record, group_record, 'GET /api/households/self')
    rtv.observe_link('User.groupId', user_record, group_record, 'GET /api/users/self')
    rtv.observe_link('User.householdId', user_record, household_record, 'GET /api/users/self')
    # Persist only selected identity evidence; UserOut.tokens and group provider
    # settings may contain secrets and must never be copied into the report.
    report = {'result': 'M1_IDENTITY_ACCEPTANCE_PASS', 'requests': statuses,
        'identity_scope_confirmed': True, 'instance_count': 3, 'observed_link_count': 3,
        'scope': scope, 'user_id': user_id,
        'permissions': {key: user[key] for key in ('admin', 'canManage', 'canManageHousehold', 'canOrganize') if isinstance(user.get(key), bool)},
        'fixtures_validated': False, 'reset_replay_validated': False, 'ready_for_live_pilot': False}
    return report, rtv.export()

def check_contract(root):
    paths = sorted((root / 'runs').glob('acceptance-*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    if not paths:
        raise AcceptanceError('No local contract acceptance was found.')
    acceptance = json.loads(paths[0].read_text(encoding='utf-8-sig'))
    if acceptance.get('result') != 'M1_SERVER_CONTRACT_READ_PASS':
        raise AcceptanceError('The latest contract acceptance is not a pass.')
    contract = Path(acceptance['contract']).resolve()
    try:
        contract.relative_to(root.resolve())
    except ValueError:
        raise AcceptanceError('Contract path is outside the project.') from None
    digest = hashlib.sha256(contract.read_bytes()).hexdigest()
    if digest != PINNED_HASH or digest != acceptance.get('sha256'):
        raise AcceptanceError('The local contract differs from the reviewed v3.28.0 contract.')
    return acceptance['baseUrl'], digest

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--username', default='changeme@example.com')
    parser.add_argument('--review-zip', required=True)
    args = parser.parse_args()
    root = Path(args.root)
    run_id = 'identity-' + datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    output = root / 'runs' / run_id
    output.mkdir(parents=True)
    report = {'result': 'M1_IDENTITY_ACCEPTANCE_FAIL', 'run_id': run_id, 'ready_for_live_pilot': False}
    runtime = None
    exit_code = 1
    try:
        base, digest = check_contract(root)
        client = LocalClient(base)
        if not sys.stdin.isatty():
            raise AcceptanceError('Run directly in an interactive terminal for hidden password input.')
        print('Login identity: ' + args.username)
        password = getpass.getpass('Mealie password (hidden): ')
        if not password:
            raise AcceptanceError('No password was supplied.')
        try:
            report, runtime = accepted_observations(client, args.username, password, run_id)
        finally:
            password = None
        report.update({'run_id': run_id, 'base_url': base, 'contract_sha256': digest})
        exit_code = 0
    except (AcceptanceError, OSError, ValueError, KeyError):
        # Do not serialize exception payloads from HTTP/authentication libraries.
        error = sys.exc_info()[1]
        report['failure'] = str(error) if isinstance(error, AcceptanceError) else 'Local configuration or response validation failed.'
    (output / 'acceptance.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    if runtime is not None:
        (output / 'rtv.json').write_text(json.dumps(runtime, indent=2) + '\n', encoding='utf-8')
    review = Path(args.review_zip)
    review.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(review, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in output.glob('*.json'):
            archive.write(path, path.name)
    print(report['result'])
    if 'failure' in report:
        print(report['failure'])
    print('Review ZIP: ' + str(review))
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
