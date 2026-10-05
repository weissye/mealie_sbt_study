"""Read existing route-campaign resources through native Provengo interfaces only."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import quote, urlsplit
from uuid import UUID
import zipfile

if __package__:
    from .relationship_execution import native, redact, failure_excerpt
    from .route_receipts import validate_route_receipts, _view
else:
    from relationship_execution import native, redact, failure_excerpt
    from route_receipts import validate_route_receipts, _view


def safe_output(value):
    value = redact(value)
    return re.sub(r"(setting\s+'audit_token'\s+to\s+')[^']*", r'\1<REDACTED_TOKEN>', value)


def member(archive, name):
    matches = [n for n in archive.namelist() if n.replace('\\', '/') == name]
    if len(matches) != 1:
        raise ValueError('Missing or ambiguous evidence member: ' + name)
    return archive.read(matches[0])


def load_campaign(path, contract):
    cases, controls, identities = [], [], set()
    contract_hash = hashlib.sha256(Path(contract).read_bytes()).hexdigest()
    with zipfile.ZipFile(path) as archive:
        summary = json.loads(member(archive, 'campaign-summary.json').decode('utf-8-sig'))
        if len(summary['runs']) != 6:
            raise ValueError('Expected the preserved six-run route campaign.')
        for run in summary['runs']:
            case, number = run['case'], run['sample']
            result = json.loads(member(archive, f'{case}/result-{number}.json'))
            payload = member(archive, f'{case}/live-{number}.zip')
            if hashlib.sha256(payload).hexdigest() != result['sha256']:
                raise ValueError('Live evidence checksum mismatch.')
            with zipfile.ZipFile(io.BytesIO(payload)) as live:
                plan = json.loads(member(live, 'relationship_scenario_plan.json'))
                acceptance = json.loads(member(live, 'execution-review/run-acceptance.json'))
                output = member(live, 'execution-review/run-output.txt').decode('utf-8')
            if plan['source_openapi_sha256'] != contract_hash:
                raise ValueError('Archived contract differs from the supplied contract.')
            if case == 'control':
                if not acceptance.get('live_accepted') or result['status'] != 'PASS':
                    raise ValueError('Original control acceptance is missing.')
                validate_route_receipts(acceptance['runtime_receipt'], plan)
                controls.append(dict(sample=number, responses=acceptance['runtime_receipt']['response_count']))
                continue
            if case not in ('rename', 'reuse') or result.get('first_failure', {}).get('stage') != 'new_route_resolution':
                raise ValueError('Unsupported failure; do not infer a route audit plan.')
            records, bodies = [], []
            for line in output.splitlines():
                match = re.search(r"RTV: setting '(rel_route_test_[^']*)' to '(.*)'$", line)
                if not match:
                    continue
                try:
                    value = json.loads(match[2])
                except ValueError:
                    continue
                if match[1].endswith('_body'):
                    bodies.append(value)
                if isinstance(value, dict) and value.get('pending'):
                    records.append(value)
            if not records or not bodies:
                raise ValueError('Missing exact pre-write evidence.')
            record, body = records[-1], bodies[-1]
            task = next(t for t in plan['tasks'] if t['kind'] == 'route_identity')
            cfg = task['config']
            before = record['pending']['before']
            if body['name'] != before['name'] or body['slug'] == before['slug']:
                raise ValueError('Evidence is not an unchanged-name direct-slug write.')
            if record['pending']['expected']['slug'] != body['slug']:
                raise ValueError('Requested route does not match the captured request.')
            if identities.intersection(record['ids']):
                raise ValueError('Resources overlap between archived runs.')
            identities.update(record['ids'])
            cases.append(dict(case=case, sample=number, config=cfg, record=record,
                              task=task, requested_slug=body['slug'], plan_metadata=plan['instance_metadata'],
                              original_result=result, submitted_body=body))
    if {(c['case'], c['sample']) for c in cases} != {(c, n) for c in ('rename', 'reuse') for n in (1, 2)}:
        raise ValueError('Missing or duplicated failed runs.')
    if {c['sample'] for c in controls} != {1, 2}:
        raise ValueError('Missing control runs.')
    return dict(campaign_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                contract_sha256=contract_hash, controls=controls, cases=cases)


def queries_for(plan):
    queries = []
    for case_index, case in enumerate(plan['cases']):
        record, task = case['record'], case['task']
        for ref in task['referrers']:
            instance = ref['instance']
            identity = record['source_ids'][instance]
            target = record['initial_targets'].get(identity)
            metadata = case['plan_metadata'][instance]
            url = ref['operation'].removeprefix('GET ')
            for slot in metadata['route_fields']:
                value = target[slot['response_field']] if target else identity
                url = url.replace('{' + slot['parameter'] + '}', quote(str(value), safe=''))
            if '{' in url or not url.startswith('/api/'):
                raise ValueError('Unresolved archived read route.')
            queries.append(dict(index=len(queries), case_index=case_index, instance=instance,
                                kind='original', path=url, expected_id=identity))
        route = next(r['operation'] for r in task['referrers'] if r['instance'] == task['targets'][0])
        slot = case['plan_metadata'][task['targets'][0]]['route_fields'][0]['parameter']
        url = route.removeprefix('GET ').replace('{' + slot + '}', quote(case['requested_slug'], safe=''))
        queries.append(dict(index=len(queries), case_index=case_index, instance=task['targets'][0],
                            kind='requested', path=url, expected_id=record['ids'][0]))
    if len(queries) != 28:
        raise ValueError('Expected 28 read-only resource requests.')
    return queries


FACTORY = r'''
function auditCallback(source){
var hydrate="if(typeof Packages!=='undefined'){Packages.org.mozilla.javascript.Context.getCurrentContext().initStandardObjects(Packages.org.mozilla.javascript.ScriptableObject.getTopLevelScope(this));}";
source=hydrate+source;
if(typeof Packages!=='undefined'){
var scope=new Packages.org.mozilla.javascript.NativeObject();
(new Packages.org.mozilla.javascript.ClassCache()).associate(scope);
return Packages.org.mozilla.javascript.Context.getCurrentContext().compileFunction(scope,"function(response,arguments){"+source+"}","read-only-audit-callback",1,null);
}
return new Function('response',source);
}
'''


def render(project, queries, base_url):
    parsed = urlsplit(base_url)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('', '/'):
        raise ValueError('Pass an HTTP server origin without credentials or path.')
    js = '//@provengo summon rest\nconst auditSvc=new RESTSession(' + json.dumps(base_url.rstrip('/')) + ',"read-only-route-audit");\n' + FACTORY
    auth_code = "var body=JSON.parse(response.body);if(response.code!==200||!body.access_token){pvg.fail('Audit authentication failed');throw new Error('Audit authentication failed');}pvg.rtv.set('audit_token',body.access_token);pvg.rtv.set('audit_observations','[]');"
    js += "function auditAuth(){auditSvc.post('/api/auth/token',{headers:{'Content-Type':'application/x-www-form-urlencoded'},body:\"grant_type=password&username=@{encodeURIComponent(getEnv('SBT_REL_USERNAME'))}&password=@{encodeURIComponent(getEnv('SBT_REL_PASSWORD'))}\",expectedResponseCodes:[200],callback:auditCallback(" + json.dumps(auth_code) + ")});}\n"
    all_reads = [dict(index=-2, path='/openapi.json'), dict(index=-1, path='/api/users/self')] + queries
    for number, query in enumerate(all_reads):
        code = "var body;try{body=JSON.parse(response.body);}catch(e){body=response.body;}"
        if query['index'] == -2:
            code += "if(response.code===200)body={version:body.info.version};"
        code += "var items=JSON.parse(pvg.rtv.get('audit_observations'));items.push({index:" + str(query['index']) + ",code:response.code,body:body});pvg.rtv.set('audit_observations',JSON.stringify(items));"
        if number == len(all_reads) - 1:
            code += "pvg.rtv.set('audit_execution_receipt',JSON.stringify({status:'READ_ONLY_CALLBACKS_COMPLETE',observations:items}));pvg.success('READ_ONLY_CALLBACKS_COMPLETE');"
        js += f'function auditRead{number}(){{auditSvc.get(' + json.dumps(query['path']) + ',{headers:{Authorization:"Bearer @{audit_token}"},expectedResponseCodes:' + json.dumps(list(range(200, 600))) + ',callback:auditCallback(' + json.dumps(code) + ')});}\n'
    stories = "bthread('read-only-route-state',function(){auditAuth();" + ''.join(f'auditRead{i}();' for i in range(len(all_reads))) + "});\n"
    (project / 'spec/js').mkdir(parents=True)
    (project / 'config').mkdir()
    (project / 'config/provengo.yml').write_text('version: 2\n')
    (project / 'spec/js/interfaces.route-audit.js').write_text(js)
    (project / 'spec/js/stories.route-audit.js').write_text(stories)


def inspect_samples(samples):
    if len(samples) != 1:
        raise ValueError('Expected one complete native audit sample.')
    rest = [e['data'] for e in samples[0] if (e.get('data') or {}).get('lib') == 'REST']
    if len(rest) != 31 or sum(e.get('method') == 'GET' for e in rest) != 30:
        raise ValueError('Incomplete read-only native sample.')
    posts = [e for e in rest if e.get('method') != 'GET']
    if len(posts) != 1 or posts[0].get('method') != 'POST' or not posts[0]['url'].endswith('/api/auth/token'):
        raise ValueError('Non-authentication mutation in audit sample.')


def receipt_from(output):
    decoder = json.JSONDecoder()
    for match in re.finditer(r"(?:SBT_ROUTE_AUDIT_RECEIPT\s+|setting\s+'audit_execution_receipt'\s+to\s+')(\{)", output):
        try:
            result, _ = decoder.raw_decode(output[match.start(1):])
        except ValueError:
            continue
        if result.get('status') == 'READ_ONLY_CALLBACKS_COMPLETE':
            return result
    raise ValueError('Complete native audit receipt was not observed.')


def classify(plan, queries, receipt, version):
    entries = receipt['observations']
    expected_indices = {-2, -1} | {q['index'] for q in queries}
    if len(entries) != len(expected_indices) or {e['index'] for e in entries} != expected_indices:
        raise ValueError('Missing or duplicate audit observations.')
    observed = {e['index']: e for e in entries}
    if observed[-2]['code'] != 200 or observed[-2]['body'].get('version') != version:
        return dict(status='SERVER_VERSION_MISMATCH', resource_mutations=0, cases=[])
    if observed[-1]['code'] != 200:
        return dict(status='AUTH_OR_SCOPE_BLOCKED', resource_mutations=0, cases=[])
    if any(e['code'] in (401, 403) for e in entries):
        return dict(status='AUTH_OR_SCOPE_BLOCKED', resource_mutations=0, cases=[])
    reports = []
    for index, case in enumerate(plan['cases']):
        checks = [q for q in queries if q['case_index'] == index]
        originals = [q for q in checks if q['kind'] == 'original']
        requested = observed[next(q['index'] for q in checks if q['kind'] == 'requested')]
        issues = []
        replacements = []
        if all(observed[q['index']]['code'] == 404 for q in originals):
            status = 'RESOURCES_NOT_PRESENT_IN_THIS_SERVER'
        elif any(observed[q['index']]['code'] != 200 for q in originals):
            status = 'PARTIAL_RESOURCES_OR_READ_ERROR'
        else:
            bodies = {q['instance']: observed[q['index']]['body'] for q in originals}
            for query in originals:
                if not isinstance(bodies[query['instance']], dict) or bodies[query['instance']].get('id') != query['expected_id']:
                    issues.append(dict(instance=query['instance'], reason='stable_identity_mismatch'))
            task, record, cfg = case['task'], case['record'], case['config']
            changed = bodies[task['targets'][0]]
            initial = record['initial_targets'][record['ids'][0]]
            if changed.get('userId') != observed[-1]['body'].get('id'):
                issues.append(dict(instance=task['targets'][0], reason='authenticated_identity_differs_from_original_owner'))
            for timestamp in cfg['timestamp_fields']:
                try:
                    datetime.fromisoformat(changed[timestamp].replace('Z', '+00:00'))
                except (KeyError, TypeError, AttributeError, ValueError):
                    issues.append(dict(instance=task['targets'][0], reason='invalid_update_timestamp'))
            replacements = []
            for path in cfg.get('recreated_identity_paths', []):
                old, new = initial, changed
                for part in path[:-5].split('.'):
                    old = old.get(part) if isinstance(old, dict) else None
                    new = new.get(part) if isinstance(new, dict) else None
                if not isinstance(old, list) or not isinstance(new, list) or len(old) != len(new):
                    issues.append(dict(instance=task['targets'][0], reason='instruction_cardinality_changed'))
                    continue
                seen = set()
                for n, (a, b) in enumerate(zip(old, new)):
                    try:
                        UUID(b['id'])
                        if b['id'] in seen:
                            raise ValueError('duplicate')
                        seen.add(b['id'])
                    except (KeyError, TypeError, AttributeError, ValueError):
                        issues.append(dict(instance=task['targets'][0], reason='invalid_or_duplicate_child_identity'))
                    if a.get('id') != b.get('id'):
                        replacements.append(dict(path=path, index=n, before=a.get('id'), after=b.get('id')))
            updated_target = {record['ids'][0]: changed}
            for instance, identity in zip(task['targets'], record['ids']):
                expected = _view(record['initial_targets'][identity], updated_target, cfg, cfg['route_field'])
                # Routing alias and recipe name must remain exactly the archived values.
                expected['slug'] = record['initial_targets'][identity]['slug']
                expected['name'] = record['initial_targets'][identity]['name']
                if expected != bodies[instance]:
                    issues.append(dict(instance=instance, reason='target_or_unrelated_state_changed'))
            for ref in task['referrers']:
                expected = _view(record['baselines'][ref['instance']], updated_target, cfg, cfg['route_field'])
                body = bodies[ref['instance']]
                projection = {f: copy.deepcopy(body[f]) for f in ref['preserve_fields'] if f in body}
                if projection != expected:
                    issues.append(dict(instance=ref['instance'], reason='reference_quantity_or_protected_view_changed'))
            if requested['code'] != 404:
                issues.append(dict(instance=task['targets'][0], reason='requested_alias_resolves_or_has_read_error', code=requested['code']))
            status = 'STATE_DISCREPANCY_REQUIRES_QUALIFICATION' if issues else 'DIRECT_SLUG_IGNORED_STATE_PRESERVED'
        reports.append(dict(case=case['case'], sample=case['sample'], status=status, issues=issues,
                            original_read_codes=[observed[q['index']]['code'] for q in originals],
                            requested_route_code=requested['code'],
                            child_identity_replacements=replacements))
    statuses = {r['status'] for r in reports}
    status = 'ORIGINAL_RESOURCES_UNAVAILABLE' if statuses == {'RESOURCES_NOT_PRESENT_IN_THIS_SERVER'} else 'READ_ONLY_STATE_AUDIT_COMPLETE'
    return dict(status=status, resource_mutations=0, new_bug_confirmed=False, cases=reports,
                limitation='Current-state reads cannot recover the original PUT response or prove absence of intervening edits.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--campaign', required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--base-url', default='http://127.0.0.1:9925')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    campaign = Path(args.campaign).resolve()
    contract = root / 'generic-generator/compatibility/contracts/mealie.json'
    project = root / 'provengo' / ('route-state-audit-' + datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f'))
    destination = Path.home() / 'Downloads' / (project.name + '.zip')
    report = dict(status='AUDIT_NOT_ACCEPTED', resource_mutations=0)
    try:
        if not re.fullmatch(r'[a-fA-F0-9]{64}', args.expected_sha256) or hashlib.sha256(campaign.read_bytes()).hexdigest() != args.expected_sha256.lower():
            raise ValueError('Original campaign SHA256 verification failed. No requests were sent.')
        plan = load_campaign(campaign, contract)
        queries = queries_for(plan)
        render(project, queries, args.base_url)
        (project / 'audit-plan.json').write_text(json.dumps(plan, indent=2))
        (project / 'queries.json').write_text(json.dumps(queries, indent=2))
        result = native(['sample', '--size', '1', '--max-length', '40', '-o', 'samples.json'], project)
        (project / 'sample-output.txt').write_text(safe_output(result.stdout + result.stderr))
        if result.returncode or not (project / 'samples.json').is_file():
            raise ValueError('Native audit sampling did not produce a sample.')
        inspect_samples(json.loads((project / 'samples.json').read_text()))
        result = native(['--batch-mode', 'run', '--run-source', 'samples.json', '--run-id', '1'], project)
        output = safe_output(result.stdout + result.stderr)
        (project / 'run-output.txt').write_text(output)
        if result.returncode:
            raise ValueError('Native audit did not complete: ' + failure_excerpt(output))
        receipt = receipt_from(output)
        (project / 'observations.json').write_text(json.dumps(receipt, indent=2))
        report = classify(plan, queries, receipt, json.loads(contract.read_text())['info']['version'])
        report.update(campaign_sha256=plan['campaign_sha256'], original_controls_verified=plan['controls'],
                      resource_reads=28, authentication_requests=1, metadata_reads=2,
                      project=str(project), review_zip=str(destination))
    except Exception as error:
        report['error'] = safe_output(str(error))
    finally:
        project.mkdir(parents=True, exist_ok=True)
        (project / 'audit-report.json').write_text(json.dumps(report, indent=2))
        destination.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
            for file in sorted(project.rglob('*')):
                if file.is_file() and file.name != 'samples.json':
                    archive.write(file, file.relative_to(project).as_posix())
        print(json.dumps(report, indent=2))
        print('Review ZIP: ' + str(destination))
    return 1 if report['status'] == 'AUDIT_NOT_ACCEPTED' else 0


if __name__ == '__main__':
    raise SystemExit(main())
