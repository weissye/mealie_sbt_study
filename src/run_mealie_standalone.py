"""Replay two generated functional stories separately against the owned local fixture."""
import argparse
import getpass
import json
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from accept_identity import AcceptanceError, accepted_observations, check_contract
from create_pilot_fixture import FixtureClient, previous_identity, require, scrub
from mealie_runtime_adapters import MealieAdapter
from sbt_generator.runtime import load_project, verify_live_contract, TypedBindings, BoundedTransport, OperationInterfaces

class StandaloneExecution:
    def __init__(self, model, samples, interfaces, adapter):
        self.model = model; self.samples = samples; self.interfaces = interfaces; self.adapter = adapter
        self.accepted = []

    def run(self):
        require([story['name'] for story in self.model['stories']] == ['recipe_description', 'list_recipe_membership'], 'This backend accepts only the two reviewed standalone stories.')
        self.adapter.establish_baseline()
        for story in self.model['stories']:
            events = [event for event in self.samples[0] if event['data']['story'] == story['name']]
            require([event['data']['id'] for event in events] == [step['id'] for step in story['steps']], 'Selected standalone order differs from the scenario IR.')
            for event in events:
                response = self.interfaces.invoke(event, self.adapter.build_payload(event))
                self.adapter.verify(event, response)
            self.adapter.accept_restoration('after_' + story['name'])
            self.accepted.append(story['name'])

def accepted_fixture(root, bindings):
    run = bindings.get('fixture_run', '')
    require(isinstance(run, str) and run.startswith('fixture-'), 'Sampled project has no accepted fixture run.')
    source = (root / 'runs' / run).resolve()
    require(source.parent == (root / 'runs').resolve(), 'Fixture run is outside the project.')
    def read(name):
        return json.loads((source / name).read_text(encoding='utf-8-sig'))
    acceptance = read('acceptance.json')
    require(acceptance.get('result') == 'M3_SERIAL_FIXTURE_ACCEPTANCE_PASS' and acceptance.get('contract_sha256') == bindings['contract_sha256'], 'Referenced fixture was not accepted for this contract.')
    require(bindings['resources'] == read('owned-resources.json') and bindings['runtime'] == read('rtv.json'), 'Sampled fixture bindings differ from the accepted fixture evidence.')
    require(len(bindings['resources']) == 14, 'The reviewed fixture must contain fourteen base resources.')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--username', default='changeme@example.com')
    parser.add_argument('--project')
    parser.add_argument('--review-zip', required=True)
    args = parser.parse_args(); root = Path(args.root).resolve()
    run_id = 'standalone-' + datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    output = root / 'runs' / run_id; output.mkdir(parents=True)
    report = {'result': 'M4_STANDALONE_STORIES_NOT_ACCEPTED', 'run_id': run_id,
              'execution_mode': 'GENERATED_EVENT_STANDALONE_REPLAY', 'live_interleavings_executed': False,
              'provengo_live_executor': False, 'reset_replay_validated': False,
              'complete_json_schema_validation': False, 'automatic_retry': False,
              'automatic_failure_rollback': False, 'live_contract_requests_sent': 0}
    client = adapter = interfaces = execution = bindings = None
    exit_code = 1
    try:
        base, digest = check_contract(root)
        project_path, model, registry, samples = load_project(root, Path(args.project) if args.project else None)
        accepted_fixture(root, registry)
        require([story['name'] for story in model['stories']] == ['recipe_description', 'list_recipe_membership'], 'Only the reviewed standalone pilot profile is implemented.')
        prior = previous_identity(root)
        require(sys.stdin.isatty(), 'Run in an interactive terminal for hidden password input.')
        client = FixtureClient(base, output)
        report['live_contract_requests_sent'] = 1
        report['live_contract'] = verify_live_contract(client, digest)
        password = getpass.getpass('Mealie password (hidden): ')
        try:
            identity_report, identity = accepted_observations(client, args.username, password, run_id)
        finally:
            password = None
        require(identity_report['scope'] == prior['scope'] and identity_report['user_id'] == prior['user_id'], 'Current actor or scope differs from accepted identity.')
        report['identity_acceptance'] = identity_report
        bindings = TypedBindings(identity, registry['resources'], registry['runtime'])
        contract = json.loads((root / 'model/mealie-openapi.v3.28.0.reviewed.json').read_text(encoding='utf-8-sig'))
        transport = BoundedTransport(client, [])
        adapter = MealieAdapter(model, contract, registry['resources'], bindings, transport, run_id)
        list_link = adapter.paths['L1'] + '/recipe/' + registry['resources']['R2']['id']
        client.owned_paths.update(adapter.paths.values()); client.link_paths.update([list_link, list_link + '/delete'])
        transport.allowed_pairs = {('GET', path) for path in adapter.paths.values()} | {
            ('PUT', adapter.paths['R2']), ('POST', list_link), ('POST', list_link + '/delete')}
        interfaces = OperationInterfaces(model, bindings, transport)
        execution = StandaloneExecution(model, samples, interfaces, adapter)
        report.update(project=str(project_path), fixture_run=registry['fixture_run'], contract_sha256=digest,
                      symbolic_schedules_verified=len(samples), actor_id=identity_report['user_id'], scope=identity_report['scope'])
        print('Replaying each generated story separately against the owned local fixture.')
        execution.run()
        report.update(result='M4_STANDALONE_RESTORATION_ACCEPTANCE_PASS',
                      stories_accepted=execution.accepted, semantic_restoration_accepted=True,
                      current_rtv_refreshed=True, active_observed_records=sum(r['state'] == 'OBSERVED' for r in bindings.rtv.records.values()),
                      active_observed_links=sum(e['state'] == 'OBSERVED' for e in bindings.rtv.edges))
        exit_code = 0
    except (AcceptanceError, OSError, ValueError, KeyError, TypeError, StopIteration):
        error = sys.exc_info()[1]
        report['failure'] = str(error) if isinstance(error, AcceptanceError) else 'Configuration or response shape was not accepted. Inspect the review package before another run.'
    finally:
        report.update(stories_accepted=execution.accepted if execution else [],
                      fixture_requests_sent=len(client.trace) if client else 0,
                      restoration_scope='Selected editable recipe content, resource content, list quantities and provenance; timestamps and generated shopping item/link IDs excluded.')
        evidence = {'acceptance.json': report}
        if interfaces:
            evidence['executed-events.json'] = interfaces.events
        if adapter:
            evidence['checkpoints.json'] = adapter.checkpoints
        if bindings:
            evidence['rtv.json'] = bindings.rtv.export()
        for name, value in evidence.items():
            (output / name).write_text(json.dumps(scrub(value), indent=2) + '\n', encoding='utf-8')
        review = Path(args.review_zip); review.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(review, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in output.glob('*.json'):
                archive.write(path, path.name)
    print(report['result'])
    if report.get('failure'):
        print(report['failure'])
        print('State may be partially changed. Review this package before retrying; no automatic recovery was sent.')
    print('Review ZIP: ' + str(review))
    print('No composed live schedules or full server reset/replay were executed.')
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
