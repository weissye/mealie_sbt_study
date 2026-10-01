"""Reviewed Mealie payloads and business oracles, separate from story scheduling."""
import copy
import json
import urllib.parse
from create_pilot_fixture import COLLECTIONS, FOODS, LISTS, CATEGORIES, TAGS, require
from sbt_generator.json_payload import project, request_schema

ENTITY_TYPES = {'F': 'Food', 'Q': 'Unit', 'C': 'Category', 'T': 'Tag', 'R': 'Recipe', 'L': 'Shopping list'}
TIME_FIELDS = {'createdAt', 'updatedAt', 'dateUpdated', 'update_at'}

def without_times(value):
    if isinstance(value, dict):
        return {k: without_times(v) for k, v in value.items() if k not in TIME_FIELDS}
    if isinstance(value, list):
        return [without_times(v) for v in value]
    return value

def canonical_list(body):
    def provenance(ref):
        return {k: ref.get(k) for k in ('recipeId', 'recipeQuantity', 'recipeScale', 'recipeNote')}
    def sorted_json(values):
        return sorted(values, key=lambda v: json.dumps(v, sort_keys=True))
    result = {k: copy.deepcopy(body.get(k)) for k in ('id', 'name', 'groupId', 'householdId', 'userId', 'extras')}
    result['recipeReferences'] = sorted_json([provenance(ref) for ref in body.get('recipeReferences', [])])
    result['listItems'] = sorted_json([{**{k: copy.deepcopy(item.get(k)) for k in
        ('foodId', 'unitId', 'labelId', 'quantity', 'checked', 'note', 'position', 'extras')},
        'recipeReferences': sorted_json([provenance(ref) for ref in item.get('recipeReferences', [])])}
        for item in body.get('listItems', [])])
    return result

class MealieAdapter:
    def __init__(self, model, contract, owned, bindings, transport, run_id):
        self.model = model; self.contract = contract; self.owned = owned
        self.recipe_update = model['operations'][model['profile']['stories'][0]['operations']['update']['operation']]
        self.bindings = bindings; self.transport = transport; self.run_id = run_id
        self.paths = {}
        for symbol, resource in owned.items():
            entity = ENTITY_TYPES.get(symbol[0])
            require(entity is not None and resource.get('name', '').startswith('mealie-sbt-'), 'Resource is outside the named pilot fixture.')
            if entity == 'Recipe':
                self.paths[symbol] = '/api/recipes/' + urllib.parse.quote(resource['slug'], safe='')
            else:
                self.paths[symbol] = COLLECTIONS[entity] + '/' + resource['id']
        self.original_recipe = None
        self.baseline = None
        self.checkpoints = []

    def canonical(self, symbol, body):
        if symbol.startswith('L'):
            return canonical_list(body)
        if symbol.startswith('R'):
            return without_times(project(body, request_schema(self.recipe_update, self.contract), self.contract))
        return without_times(copy.deepcopy(body))

    def capture(self, label):
        bodies = {}
        for symbol, path in self.paths.items():
            body = self.transport.call('GET', path)
            require(isinstance(body, dict), 'Expected a resource object during baseline capture.')
            self.bindings.observe(ENTITY_TYPES[symbol[0]], symbol, body, 'GET ' + path)
            bodies[symbol] = body
        self.refresh_relationships(bodies)
        self.current_bodies = copy.deepcopy(bodies)
        state = {symbol: self.canonical(symbol, body) for symbol, body in bodies.items()}
        self.checkpoints.append({'label': label, 'state': state, 'rtv': self.bindings.rtv.export()})
        return state, bodies

    def refresh_relationships(self, bodies):
        runtime = self.bindings.rtv
        nested = {'Recipe ingredient', 'Shopping item', 'List-recipe link', 'Item-recipe link'}
        for record in runtime.records.values():
            if record['entity_type'] in nested:
                record['state'] = 'STALE_AFTER_REFRESH'
        for edge in runtime.edges:
            if edge['relation'] not in ('Household.groupId', 'User.groupId', 'User.householdId'):
                edge['state'] = 'STALE_AFTER_REFRESH'
        by_recipe = {body['id']: symbol for symbol, body in bodies.items() if symbol.startswith('R')}
        by_food = {body['id']: symbol for symbol, body in bodies.items() if symbol.startswith('F')}
        by_unit = {body['id']: symbol for symbol, body in bodies.items() if symbol.startswith('Q')}
        def observe(entity, symbol, scope, identifiers, source):
            record = runtime.observe(entity, symbol, scope, identifiers, source)
            runtime.records[record]['state'] = 'OBSERVED'
            return record
        def edge(relation, source, target, evidence):
            for prior in runtime.edges:
                if (prior['relation'], prior['source'], prior['target']) == (relation, source, target):
                    prior['state'] = 'OBSERVED'; prior['evidence'] = evidence
                    return
            runtime.observe_link(relation, source, target, evidence)
        for symbol, body in bodies.items():
            source = 'GET ' + self.paths[symbol]
            if symbol.startswith('R'):
                for item in body.get('recipeIngredient', []):
                    require(item.get('food', {}).get('id') in by_food and item.get('unit', {}).get('id') in by_unit and item.get('referencedRecipe') is None, 'Recipe ingredient is outside the accepted simple pilot.')
                    record = observe('Recipe ingredient', symbol + ':' + item['referenceId'], {**self.bindings.scope, 'recipe': body['id']}, {'referenceId': item['referenceId']}, source)
                    edge('Recipe.ingredient', self.bindings.records[symbol], record, source)
                    edge('Ingredient.food', record, self.bindings.records[by_food[item['food']['id']]], source)
                    edge('Ingredient.unit', record, self.bindings.records[by_unit[item['unit']['id']]], source)
                for field, relation, prefix in [('recipeCategory', 'Recipe.category', 'C'), ('tags', 'Recipe.tag', 'T')]:
                    by_id = {v['id']: k for k, v in bodies.items() if k.startswith(prefix)}
                    for item in body.get(field, []):
                        require(item['id'] in by_id, 'Recipe classification is outside the owned fixture.')
                        edge(relation, self.bindings.records[symbol], self.bindings.records[by_id[item['id']]], source)
            if symbol.startswith('L'):
                scope = {**self.bindings.scope, 'shoppingList': body['id']}
                for ref in body.get('recipeReferences', []):
                    require(ref.get('shoppingListId') == body['id'] and ref.get('recipeId') in by_recipe, 'List-recipe endpoints differ from owned resources.')
                    record = observe('List-recipe link', symbol + ':link:' + ref['id'], scope, {'id': ref['id']}, source)
                    edge('List.link', self.bindings.records[symbol], record, source)
                    edge('List-recipe link.recipe', record, self.bindings.records[by_recipe[ref['recipeId']]], source)
                for item in body.get('listItems', []):
                    require(item.get('shoppingListId') == body['id'] and item.get('foodId') in by_food and item.get('unitId') in by_unit, 'Shopping item parent, food or unit differs.')
                    require(item.get('groupId') == self.bindings.scope['group'] and item.get('householdId') == self.bindings.scope['household'], 'Shopping item scope differs.')
                    record = observe('Shopping item', symbol + ':item:' + item['id'], scope, {'id': item['id']}, source)
                    edge('List.item', self.bindings.records[symbol], record, source)
                    edge('Shopping item.food', record, self.bindings.records[by_food[item['foodId']]], source)
                    edge('Shopping item.unit', record, self.bindings.records[by_unit[item['unitId']]], source)
                    for ref in item.get('recipeReferences', []):
                        require(ref.get('shoppingListItemId') == item['id'] and ref.get('recipeId') in by_recipe, 'Item-recipe endpoints differ.')
                        link = observe('Item-recipe link', symbol + ':item-link:' + ref['id'], scope, {'id': ref['id']}, source)
                        edge('Shopping item.link', record, link, source)
                        edge('Item-recipe link.recipe', link, self.bindings.records[by_recipe[ref['recipeId']]], source)

    def establish_baseline(self):
        self.baseline, bodies = self.capture('before_stories')
        self.original_recipe = copy.deepcopy(bodies['R2'])
        for symbol, foods in FOODS.items():
            recipe = bodies[symbol]
            ingredients = recipe.get('recipeIngredient', [])
            expected_pairs = {(self.owned[food]['id'], self.owned['Q2' if food == 'F3' else 'Q1']['id']) for food in foods}
            require(len(ingredients) == 2 and {(x['food']['id'], x['unit']['id']) for x in ingredients} == expected_pairs and all(x.get('quantity') == 1 for x in ingredients), 'Recipe baseline ingredients differ from the accepted unit-quantity fixture.')
            require(recipe.get('recipeServings') == 2 and recipe.get('recipeYieldQuantity') == 2, 'Recipe baseline serving/yield quantities differ.')
            require({x['id'] for x in recipe.get('recipeCategory', [])} == {self.owned[x]['id'] for x in CATEGORIES[symbol]} and {x['id'] for x in recipe.get('tags', [])} == {self.owned[x]['id'] for x in TAGS[symbol]}, 'Recipe baseline classifications differ.')
        for symbol, recipe_symbols in LISTS.items():
            refs = bodies[symbol].get('recipeReferences', [])
            require(len(refs) == 2 and {ref['recipeId'] for ref in refs} == {self.owned[r]['id'] for r in recipe_symbols} and all(ref.get('recipeQuantity') == 1 for ref in refs), 'List baseline does not match the accepted one-copy fixture.')
            expected = {}
            for recipe in recipe_symbols:
                for food in FOODS[recipe]:
                    key = (self.owned[food]['id'], self.owned['Q2' if food == 'F3' else 'Q1']['id'])
                    expected.setdefault(key, []).append(self.owned[recipe]['id'])
            items = bodies[symbol]['listItems']
            require(len(items) == len(expected), 'List baseline contains duplicate or unexpected food/unit items.')
            for item in items:
                key = (item['foodId'], item['unitId'])
                require(key in expected and item['quantity'] == len(expected[key]) and sorted(r['recipeId'] for r in item['recipeReferences']) == sorted(expected[key]), 'List baseline quantities or provenance differ.')
                require(not item.get('checked') and item.get('note', '') == '' and item.get('position', 0) == 0 and item.get('labelId') is None and not item.get('extras'), 'List baseline contains edited item fields outside the accepted restoration profile.')
                require(all(ref.get('recipeQuantity') == 1 and ref.get('recipeScale') == 1 and ref.get('recipeNote') is None for ref in item['recipeReferences']), 'List baseline recipe provenance quantities differ.')
        self.marker = 'Standalone functional acceptance ' + self.run_id

    def build_payload(self, event):
        data = event['data']; action = data['action']
        if action not in ('update', 'restore', 'remove_link', 'add_link'):
            return None
        operation = self.model['operations'][data['operation']]
        schema = request_schema(operation, self.contract)
        if action in ('update', 'restore'):
            payload = project(self.original_recipe, schema, self.contract)
            payload['description'] = self.marker if action == 'update' else self.original_recipe.get('description')
        else:
            field = 'recipeDecrementQuantity' if action == 'remove_link' else 'recipeIncrementQuantity'
            payload = {field: 1}
        return project(payload, schema, self.contract)

    def verify(self, event, body):
        data = event['data']; action = data['action']
        if data['story'] == 'recipe_description' and action in ('capture', 'verify_update'):
            self.bindings.observe('Recipe', 'R2', body, 'GET ' + self.paths['R2'])
            expected = copy.deepcopy(self.baseline['R2'])
            if action == 'verify_update':
                expected['description'] = self.marker
            require(self.canonical('R2', body) == expected, 'Recipe readback differs beyond the intended description change.')
        if data['story'] == 'list_recipe_membership' and action in ('verify_absent', 'verify_present'):
            self.bindings.observe('Shopping list', 'L1', body, 'GET ' + self.paths['L1'])
            recipe = self.owned['R2']['id']
            if action == 'verify_absent':
                require(all(ref.get('recipeId') != recipe for ref in body.get('recipeReferences', [])), 'Removed recipe is still present in list-level provenance.')
                require(all(ref.get('recipeId') != recipe for item in body.get('listItems', []) for ref in item.get('recipeReferences', [])), 'Removed recipe is still present in item-level provenance.')
                expected = copy.deepcopy(self.baseline['L1'])
                expected['recipeReferences'] = [ref for ref in expected['recipeReferences'] if ref['recipeId'] != recipe]
                retained = []
                for item in expected['listItems']:
                    removed = [ref for ref in item['recipeReferences'] if ref['recipeId'] == recipe]
                    item['recipeReferences'] = [ref for ref in item['recipeReferences'] if ref['recipeId'] != recipe]
                    if item['recipeReferences']:
                        item['quantity'] -= len(removed)
                        retained.append(item)
                expected['listItems'] = retained
                require(self.canonical('L1', body) == expected, 'Unlinked list does not preserve the other recipe quantities/provenance.')
                other = self.transport.call('GET', self.paths['L2'])
                self.bindings.observe('Shopping list', 'L2', other, 'GET ' + self.paths['L2'])
                require(self.canonical('L2', other) == self.baseline['L2'], 'Unlinking from L1 changed the other parent L2.')
                self.current_bodies.update({'L1': copy.deepcopy(body), 'L2': copy.deepcopy(other)})
                self.refresh_relationships(self.current_bodies)
                self.checkpoints.append({'label': 'membership_absent', 'state': {symbol: self.canonical(symbol, resource) for symbol, resource in self.current_bodies.items()}, 'rtv': self.bindings.rtv.export()})
            else:
                require(self.canonical('L1', body) == self.baseline['L1'], 'Re-linked list differs in quantities, provenance or selected item fields.')

    def accept_restoration(self, label):
        state, _ = self.capture(label)
        require(state == self.baseline, 'Selected semantic state was not restored after ' + label)
