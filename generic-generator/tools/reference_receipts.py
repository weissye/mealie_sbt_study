"""Independent reference-lifecycle receipt checks; never sends HTTP."""
import copy


def _replace(value,path,target,replacement):
    name,*rest=path.split('.')
    array=name.endswith('[]');name=name.removesuffix('[]')
    if not isinstance(value,dict):raise ValueError('Invalid protected relationship container.')
    if rest:
        children=value.get(name,[]) if array else [value.get(name)]
        for child in children:_replace(child,'.'.join(rest),target,replacement)
    else:
        leaf=value.get(name)
        identity=leaf.get('id',leaf.get('slug')) if isinstance(leaf,dict) else leaf
        if identity==target:value[name]=copy.deepcopy(replacement)


def _rebind_slots(value,baseline,path,target,replacement):
    name,*rest=path.split('.')
    array=name.endswith('[]');name=name.removesuffix('[]')
    if rest:
        if array:
            if len(value[name])!=len(baseline[name]):raise ValueError('Followup changed occurrence count.')
            for v,b in zip(value[name],baseline[name]):_rebind_slots(v,b,'.'.join(rest),target,replacement)
        else:_rebind_slots(value[name],baseline[name],'.'.join(rest),target,replacement)
    else:
        leaf=baseline.get(name);identity=leaf.get('id',leaf.get('slug')) if isinstance(leaf,dict) else leaf
        if identity==target:value[name]=copy.deepcopy(replacement)


def validate_reference_receipts(receipt,plan):
    tasks={t['id']:t for t in plan['tasks'] if t['kind']=='reference_lifecycle'}
    if not tasks:return
    records=receipt.get('reference_lifecycles')
    if not isinstance(records,list) or len(records)!=len(tasks):raise ValueError('Missing reference lifecycle receipt.')
    seen=set()
    for record in records:
        task=tasks.get(record.get('task_id')) if isinstance(record,dict) else None
        if not task or task['id'] in seen:raise ValueError('Duplicate or unknown reference lifecycle.')
        rule=task['rule'];seen.add(task['id'])
        if record.get('target')!=task['source_instance'] or not record.get('target_id') or record.get('target_checked') is not True:raise ValueError('Unobserved reference target.')
        if rule['mode']=='control':
            if record.get('deleted') is not False or record.get('delete_code') is not None or record.get('outcome')!='CONTROL_NO_DELETE':raise ValueError('Control unexpectedly deletes.')
        elif record.get('deleted') is True:
            if not isinstance(record.get('delete_code'),int) or not 200<=record['delete_code']<300 or record.get('outcome')!='SUCCESS_NULL_POLICY_OBSERVED':raise ValueError('Invalid success branch.')
        elif record.get('deleted') is False:
            if record.get('delete_code') not in rule['rejection_codes'] or record.get('outcome')!='REJECTION_UNCHANGED_POLICY_OBSERVED':raise ValueError('Invalid rejection branch.')
        else:raise ValueError('Deletion outcome missing.')
        reads=record.get('target_reads',[])
        if not isinstance(reads,list) or len(reads)!=2:raise ValueError('Missing target readbacks before/after followup.')
        for read in reads:
            if record['deleted']:
                if read.get('code') not in rule['absence_codes'] or read.get('observed') is not None:raise ValueError('Target absence was not observed twice.')
            elif read.get('code')!=200 or not isinstance(record.get('target_before'),dict) or read.get('observed')!=record['target_before']:raise ValueError('Retained target changed.')
        checks=record.get('checks',[])
        if len(checks)!=len(task['checks']):raise ValueError('Missing source/control checks.')
        instances=[]
        for check in checks:
            configured=next((c for c in task['checks'] if c['instance']==check.get('instance')),None)
            if not configured or check.get('referrer') is not configured['referrer'] or check.get('field_path')!=configured['field_path']:raise ValueError('Wrong reference check.')
            before=check.get('before');expected=copy.deepcopy(before)
            if not isinstance(before,dict) or sorted(before)!=sorted(configured['preserve_fields']):raise ValueError('Incomplete protected fields.')
            if configured['referrer']:
                # A receipt may not claim sharing without presenting the target in its baseline.
                probe=copy.deepcopy(before);_replace(probe,configured['field_path'],record['target_id'],None)
                if probe==before:raise ValueError('Shared dependency was not observed.')
            if record['deleted'] and configured['field_path']:_replace(expected,configured['field_path'],record['target_id'],None)
            if check.get('expected')!=expected or check.get('observed')!=expected:raise ValueError('Reference lifecycle state mismatch.')
            instances.append(configured['instance'])
        if sorted(instances)!=sorted(c['instance'] for c in task['checks']):raise ValueError('Duplicate source check.')
        followups=record.get('followups',[])
        if [f.get('stage') for f in followups]!=['update','rebind']:raise ValueError('Missing followup update/rebind.')
        for f in followups:
            if f.get('instance')!=task['followup_source'] or not isinstance(f.get('expected'),dict) or f['expected']!=f.get('observed'):raise ValueError('Unverified followup.')
        update=followups[0]
        if update.get('field')!=rule['update_field'] or not update.get('expected_value') or update['expected_value']!=update.get('value'):raise ValueError('Followup field did not update.')

        source_check=next(c for c in checks if c['instance']==task['followup_source'])
        if update['expected']!=source_check['observed']:raise ValueError('Followup does not preserve its observed baseline.')
        replacement=record.get('replacement_value')
        owned=next((o for o in receipt.get('owned_records',[]) if o.get('instance')==task['replacement']),None)
        if not isinstance(replacement,dict) or not owned or replacement.get('id')!=record.get('replacement_id') or owned.get('route',{}).get('id')!=record['replacement_id']:raise ValueError('Replacement identity is not owned.')
        expected_rebind=copy.deepcopy(update['observed'])
        _rebind_slots(expected_rebind,source_check['before'],rule['field_path'],record['target_id'],replacement)
        if followups[1]['expected']!=expected_rebind:raise ValueError('Rebind expectation is not derived from observed slots.')
