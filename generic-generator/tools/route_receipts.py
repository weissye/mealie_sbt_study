"""Independent route change receipt validation. No HTTP requests."""
import copy
from datetime import datetime


def _view(value,targets,cfg,change):
    value=copy.deepcopy(value)
    def walk(o):
        if isinstance(o,dict):
            target=targets.get(o.get(cfg['identity_field']))
            if target:
                for field in [cfg['route_field'],change]+cfg['timestamp_fields']:
                    if field in o and field in target:o[field]=target[field]
            for child in o.values():walk(child)
        elif isinstance(o,list):
            for child in o:walk(child)
    walk(value);return value


def validate_route_receipts(receipt,plan):
    tasks=[t for t in plan['tasks'] if t['kind']=='route_identity']
    if not tasks:return
    records=receipt.get('route_identities',[])
    if len(records)!=len(tasks):raise ValueError('Missing route receipts.')
    owned={o['instance']:o['route'] for o in receipt['owned_records']};seen=set()
    for record in records:
        task=next((t for t in tasks if t['id']==record.get('task_id')),None)
        if task is None or task['id'] in seen:raise ValueError('Unknown/duplicate route task.')
        seen.add(task['id']);cfg=task['config'];field=cfg['route_field'];identity=cfg['identity_field'];change=task['change_field'];ids=record['ids']
        if len(ids)!=3 or len(set(ids))!=3 or ids!=[owned[t][identity] for t in task['targets']]:raise ValueError('Route stable identities not owned.')
        targets=copy.deepcopy(record['initial_targets']);initial=record['initial_routes'];baselines=record['baselines']
        if set(targets)!=set(ids) or initial!=[targets[i][field] for i in ids]:raise ValueError('Invalid initial aliases.')
        refs=task['referrers']
        if set(baselines)!={r['instance'] for r in refs} or record['source_ids']!={r['instance']:owned[r['instance']][identity] for r in refs}:raise ValueError('Invalid referrer ownership.')
        if not isinstance(record.get('namespace'),str) or not record['namespace']:raise ValueError('Missing route namespace.')
        def values(value,path):
            parts=path.split('.');current=[value]
            for part in parts:
                array=part.endswith('[]');key=part.removesuffix('[]');following=[]
                for node in current:
                    if isinstance(node,dict) and key in node:
                        item=node[key];following.extend(item if array and isinstance(item,list) else [item])
                current=following
            return current
        for ref in refs:
            before=baselines[ref['instance']]
            if set(before)-set(ref['preserve_fields']):raise ValueError('Unknown protected baseline fields.')
            if ref.get('requires_reference') and ids[0] not in values(before,ref['reference_path']):raise ValueError('Initial referrer not linked to original target.')
        if len(record['phases'])!=len(task['phases']):raise ValueError('Incomplete route phases.')
        expected_alias=[]
        for n,(actual,phase) in enumerate(zip(record['phases'],task['phases'])):
            id=ids[phase['target_index']-1];before=targets[id];value=initial[phase['reuse_index']-1] if 'reuse_index' in phase else record['namespace']+'-'+phase['suffix'];expected=copy.deepcopy(before);expected[change]=value
            observed=actual.get('observed');protected=copy.deepcopy(observed)
            if not isinstance(observed,dict):raise ValueError('Missing route target observation.')
            for timestamp in cfg['timestamp_fields']:
                try:datetime.fromisoformat(observed[timestamp].replace('Z','+00:00'))
                except (KeyError,TypeError,AttributeError,ValueError) as e:raise ValueError('Invalid observed timestamp.') from e
                if timestamp in expected:protected[timestamp]=expected[timestamp]
                else:protected.pop(timestamp,None)
            if actual.get('phase')!=phase or actual.get('before')!=before or actual.get('expected')!=expected or actual.get('value')!=value or protected!=expected:raise ValueError('Route identity or protected state mismatch.')
            targets[id]=copy.deepcopy(observed)
            checks=actual.get('checks',[])
            if sorted(c['instance'] for c in checks)!=sorted(r['instance'] for r in refs):raise ValueError('Missing/duplicate referrer check.')
            for check in checks:
                expected_view=_view(baselines[check['instance']],targets,cfg,change)
                if check['expected']!=expected_view or check['observed']!=expected_view:raise ValueError('Reference migrated or quantity changed.')
            expected_id=id if cfg['mode']=='control' else None
            expected_alias.append({'phase':n,'code':200 if expected_id else 404,'expected_id':expected_id,'observed_id':expected_id})
        if cfg['mode']=='reuse':expected_alias.append({'phase':2,'code':200,'expected_id':ids[2],'observed_id':ids[2]})
        if record['alias_checks']!=expected_alias or record['targets']!=targets:raise ValueError('Incorrect final alias resolution.')
        for id,target in zip(ids,task['targets']):
            if owned[target].get(field)!=targets[id][field]:raise ValueError('Final route binding is stale.')
