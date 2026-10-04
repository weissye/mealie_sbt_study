"""Verify frozen evidence offline. No API requests or resource mutations."""
import copy
import hashlib
import io
import json
import re
import zipfile
import sys
from pathlib import Path
from semantic_receipts import validate_semantic_receipts

root = Path(sys.argv[1]).resolve()
checksums = {'campaign.zip': '018e226d5d37796048b7af3879d266cbe8c133b400a071f39d451ba4f3bc891b', 'mealie_collision_confirmation_2_20261004-145853.zip': '7fd55883b9f2920f05520f64c6a12df21539b5fdceaca40ab38ed1f4d062901a'}
for name, expected in checksums.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name

def inspect(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        plan = json.loads(archive.read('relationship_scenario_plan.json'))
        lines = archive.read('execution-review/run-output.txt').decode('utf-8-sig').splitlines()
    values = {}
    for line in lines:
        match = re.search(r"RTV: setting '([^']+)' to '(.*)'$", line)
        if match:
            try:
                values[match[1]] = json.loads(match[2])
            except ValueError:
                pass
    records = values['sbt_rel_semantic_receipts']
    completed = {r['task_id'] for r in records}
    prefix = copy.deepcopy(plan)
    prefix['tasks'] = [t for t in plan['tasks'] if not t['kind'].startswith('semantic_') or t['id'] in completed]
    validate_semantic_receipts({'semantic_tests': records, 'owned_records': values['sbt_rel_owned']}, prefix)
    task_id = 'semantic:11:contribution:api/households/shopping/lists#1'
    pending = next(v for k, v in values.items() if k.endswith('_semantic') and isinstance(v, dict) and v.get('task_id') == task_id)
    task = next(t for t in plan['tasks'] if t['id'] == task_id)
    assert pending['amount'] == task['amount'] == 0.5
    recipe = pending['reference_instance']
    container = pending['container']
    observation = next(c['observed'] for c in pending['checks'] if c['instance'] == recipe)
    assert observation == pending['before'][recipe]
    key = next(iter(observation['totals']))
    before = pending['before'][container]['totals'][key]
    quantity = observation['totals'][key]
    expected = before + pending['amount'] * quantity
    warning = next(line for line in lines if ' WARN [' in line and 'FAIL: Semantic consistency mismatch:' in line)
    failure = json.loads(warning.split('FAIL: Semantic consistency mismatch: ', 1)[1].removesuffix('.'))
    assert failure['instance'] == container
    assert failure['expected']['references'] == failure['observed']['references']
    assert failure['expected']['totals'][key] == expected == 19
    assert failure['observed']['totals'][key] == 20
    return {'completed_semantic_tasks': len(records), 'order': [r['task_id'] for r in records], 'recipe_id': pending['reference_id'], 'before': before, 'recipe_quantity': quantity, 'increment': pending['amount'], 'expected': expected, 'observed': 20, 'prefix_validation': 'PASS'}

with zipfile.ZipFile(root / 'campaign.zip') as archive:
    first = inspect(archive.read('live-1.zip'))
second = inspect((root / 'mealie_collision_confirmation_2_20261004-145853.zip').read_bytes())
assert first['recipe_id'] != second['recipe_id']
assert first['order'] != second['order']
print(json.dumps({'status': 'REPEATED_SEMANTIC_DISCREPANCY_VERIFIED', 'server_requests': 0, 'different_owned_resources': True, 'different_semantic_orders': True, 'runs': [first, second], 'root_cause_confirmed': False, 'reset_replay_validated': False}, indent=2))
