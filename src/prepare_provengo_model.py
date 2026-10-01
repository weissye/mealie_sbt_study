"""Generate an offline symbolic model from an accepted local fixture."""
import argparse
import hashlib
import json
import uuid
from pathlib import Path
from accept_identity import PINNED_HASH

from sbt_generator.pipeline import compile_model, render_stories, emit

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

def compiled_model(root=DEFAULT_ROOT):
    return compile_model(root / 'model/mealie-openapi.v3.28.0.reviewed.json', root / 'profiles/mealie-pilot.json')

def enumerate_orders(stories):
    chains = [[step['id'] for step in story['steps']] for story in stories]
    result = []
    def visit(positions, sequence):
        if len(result) >= 10000:
            raise ValueError('Offline exhaustive schedule budget exceeded (10000).')
        if all(positions[i] == len(chain) for i, chain in enumerate(chains)):
            result.append(sequence)
            return
        for index, chain in enumerate(chains):
            if positions[index] < len(chain):
                next_positions = positions[:]
                next_positions[index] += 1
                visit(next_positions, sequence + [chain[positions[index]]])
    visit([0] * len(chains), [])
    return result

def orders():
    return enumerate_orders(compiled_model()['stories'])

def model_js():
    return render_stories(compiled_model())


def prepare(root):
    candidates = sorted((root / 'runs').glob('fixture-*/acceptance.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise ValueError('No fixture acceptance report was found.')
    acceptance = json.loads(candidates[0].read_text(encoding='utf-8-sig'))
    if acceptance.get('result') != 'M3_SERIAL_FIXTURE_ACCEPTANCE_PASS' or acceptance.get('contract_sha256') != PINNED_HASH:
        raise ValueError('The latest fixture is not an accepted fixture for the reviewed contract.')
    source = candidates[0].parent
    owned = json.loads((source / 'owned-resources.json').read_text(encoding='utf-8-sig'))
    runtime = json.loads((source / 'rtv.json').read_text(encoding='utf-8-sig'))
    if len(owned) != 14 or not all(key in owned for key in ('R1', 'R2', 'R3', 'L1', 'L2')):
        raise ValueError('The accepted resource registry does not contain the expected fixture.')
    types = {'F': 'Food', 'Q': 'Unit', 'C': 'Category', 'T': 'Tag', 'R': 'Recipe', 'L': 'Shopping list'}
    for symbol, value in owned.items():
        matches = [record for record in runtime['records'].values() if symbol in record['symbols'] and record['entity_type'] == types.get(symbol[0])]
        if len(matches) != 1 or matches[0]['identifiers'].get('id') != value.get('id') or matches[0]['state'] != 'OBSERVED':
            raise ValueError('An owned resource differs from its typed RTV binding: ' + symbol)
        if value.get('slug') and matches[0]['identifiers'].get('slug') != value['slug']:
            raise ValueError('An observed slug differs from the owned resource binding: ' + symbol)
    raw_contract = (root / 'model/mealie-openapi.v3.28.0.reviewed.json').read_bytes()
    if hashlib.sha256(raw_contract).hexdigest() != PINNED_HASH:
        raise ValueError('The reviewed contract file changed.')
    model = compiled_model(root)
    stories = model['stories']
    for story in stories:
        for step in story['steps']:
            for binding in step['bindings'].values():
                entity_type, identifier = binding['type'].rsplit('.', 1)
                matches = [record for record in runtime['records'].values()
                           if binding['symbol'] in record['symbols'] and record['entity_type'] == entity_type
                           and record['state'] == 'OBSERVED' and identifier in record['identifiers']]
                if len(matches) != 1:
                    raise ValueError('Scenario binding lacks one observed typed identity: ' + binding['symbol'])
    expected_orders = enumerate_orders(stories)
    project = root / 'provengo' / ('offline-' + uuid.uuid4().hex[:12])
    (project / 'spec' / 'js').mkdir(parents=True)
    (project / 'config').mkdir()
    (project / 'config' / 'provengo.yml').write_text('version: 2\n', encoding='utf-8')
    emit(model, project)
    (project / 'expected-orders.json').write_text(json.dumps(expected_orders, indent=2) + '\n', encoding='utf-8')
    (project / 'fixture-bindings.json').write_text(json.dumps({'fixture_run': acceptance['run_id'],
        'contract_sha256': PINNED_HASH, 'resources': owned, 'runtime': runtime}, indent=2) + '\n', encoding='utf-8')
    (project / 'model-plan.json').write_text(json.dumps({'stage': 'M4_OFFLINE_MODEL_READY', 'stories': stories,
        'expected_symbolic_order_count': len(expected_orders), 'transport': 'none; symbolic sampling only',
        'runtime_executor_implemented': False, 'standalone_mutation_stories_accepted': False,
        'reset_replay_validated': False, 'actual_parallel_http': False,
        'next_gate': 'Accept each functional story and its restoration against the owned fixture before live composition.'}, indent=2) + '\n', encoding='utf-8')
    return project

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--root', required=True)
    args = parser.parse_args()
    project = prepare(Path(args.root))
    print(json.dumps({'project': str(project.resolve()), 'expected_order_count': len(json.loads((project / 'expected-orders.json').read_text()))}))

if __name__ == '__main__':
    main()
