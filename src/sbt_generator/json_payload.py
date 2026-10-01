"""Bounded JSON input projection for the reviewed OpenAPI schema subset.

This is a request projector, not a complete JSON Schema validator.
"""
import copy
import math
import uuid
from accept_identity import AcceptanceError

def resolve(schema, contract):
    seen = set()
    while '$ref' in schema:
        ref = schema['$ref']
        if not ref.startswith('#/') or ref in seen:
            raise AcceptanceError('Unsupported or cyclic direct schema reference.')
        seen.add(ref)
        target = contract
        for part in ref[2:].split('/'):
            target = target[part.replace('~1', '/').replace('~0', '~')]
        schema = {**target, **{k: v for k, v in schema.items() if k != '$ref'}}
    return schema

def project(value, schema, contract, depth=0):
    if depth > 40:
        raise AcceptanceError('Request projection exceeded the schema depth bound.')
    schema = resolve(schema, contract)
    if 'anyOf' in schema or 'oneOf' in schema:
        key = 'anyOf' if 'anyOf' in schema else 'oneOf'
        candidates = []
        for branch in schema[key]:
            try:
                candidates.append(project(value, {**{k: v for k, v in schema.items() if k != key}, **branch}, contract, depth + 1))
            except AcceptanceError:
                pass
        if not candidates or (key == 'oneOf' and len(candidates) != 1):
            raise AcceptanceError('Request does not match the documented union branches.')
        return candidates[0]
    if 'allOf' in schema:
        raise AcceptanceError('allOf input projection is not accepted by this backend yet.')
    kind = schema.get('type')
    valid = {'null': value is None, 'object': isinstance(value, dict), 'array': isinstance(value, list),
             'string': isinstance(value, str), 'boolean': isinstance(value, bool),
             'integer': isinstance(value, int) and not isinstance(value, bool),
             'number': isinstance(value, (int, float)) and not isinstance(value, bool)}
    if kind in valid and not valid[kind]:
        raise AcceptanceError('Request value has the wrong JSON type: ' + kind)
    if 'enum' in schema and value not in schema['enum']:
        raise AcceptanceError('Request value is outside the documented enum.')
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(value):
            raise AcceptanceError('Non-finite request number.')
        for key, wrong in [('minimum', lambda x: value < x), ('maximum', lambda x: value > x),
                           ('exclusiveMinimum', lambda x: value <= x), ('exclusiveMaximum', lambda x: value >= x)]:
            if key in schema and wrong(schema[key]):
                raise AcceptanceError('Request number exceeds a documented bound.')
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0) or len(value) > schema.get('maxLength', float('inf')):
            raise AcceptanceError('Request string length exceeds a documented bound.')
        if schema.get('format') in ('uuid', 'uuid4'):
            try:
                parsed = uuid.UUID(value)
                if schema['format'] == 'uuid4' and parsed.version != 4:
                    raise ValueError()
            except ValueError:
                raise AcceptanceError('Request UUID format differs from the contract.') from None
    if isinstance(value, list) and (kind == 'array' or 'items' in schema):
        if len(value) < schema.get('minItems', 0) or len(value) > schema.get('maxItems', float('inf')):
            raise AcceptanceError('Request array length exceeds a documented bound.')
        return [project(x, schema.get('items', {}), contract, depth + 1) for x in value]
    if isinstance(value, dict) and (kind == 'object' or 'properties' in schema):
        properties = schema.get('properties', {})
        result = {}
        for key, item in value.items():
            if key in properties:
                if not properties[key].get('readOnly'):
                    result[key] = project(item, properties[key], contract, depth + 1)
            elif schema.get('additionalProperties') is True:
                result[key] = copy.deepcopy(item)
            elif isinstance(schema.get('additionalProperties'), dict):
                result[key] = project(item, schema['additionalProperties'], contract, depth + 1)
        for key in schema.get('required', []):
            if key not in result and not properties.get(key, {}).get('readOnly'):
                raise AcceptanceError('Missing required request property: ' + key)
        return result
    return copy.deepcopy(value)

def request_schema(operation, contract):
    source = contract
    for part in operation['pointer'][2:].split('/'):
        source = source[part.replace('~1', '/').replace('~0', '~')]
    body = resolve(source.get('requestBody', {}), contract)
    content = body.get('content', {})
    if 'application/json' not in content:
        raise AcceptanceError('Selected mutation has no documented JSON input variant.')
    return content['application/json']['schema']
