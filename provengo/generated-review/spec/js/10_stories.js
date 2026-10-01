// Generated from scenario IR. No paths, methods or REST details.
bthread("recipe_description", function () {
    SBTInterfaces.invoke("get_one_api_recipes__slug__get", {"bindings":{"slug":{"symbol":"R2","type":"Recipe.slug"}},"id":"A1","action":"capture","story":"recipe_description","actor":"U1","mode":"SYMBOLIC_ONLY"});
    SBTInterfaces.invoke("update_one_api_recipes__slug__put", {"bindings":{"slug":{"symbol":"R2","type":"Recipe.slug"}},"id":"A2","action":"update","story":"recipe_description","actor":"U1","mode":"SYMBOLIC_ONLY"});
    SBTInterfaces.invoke("get_one_api_recipes__slug__get", {"bindings":{"slug":{"symbol":"R2","type":"Recipe.slug"}},"id":"A3","action":"verify_update","story":"recipe_description","actor":"U1","mode":"SYMBOLIC_ONLY"});
    SBTInterfaces.invoke("update_one_api_recipes__slug__put", {"bindings":{"slug":{"symbol":"R2","type":"Recipe.slug"}},"id":"A4","action":"restore","story":"recipe_description","actor":"U1","mode":"SYMBOLIC_ONLY"});
});
bthread("list_recipe_membership", function () {
    SBTInterfaces.invoke("remove_recipe_ingredients_from_list_api_households_shopping_lists__item_id__recipe__recipe_id__delete_post", {"bindings":{"item_id":{"symbol":"L1","type":"Shopping list.id"},"recipe_id":{"symbol":"R2","type":"Recipe.id"}},"id":"B1","action":"remove_link","story":"list_recipe_membership","actor":"U1","mode":"SYMBOLIC_ONLY"});
    SBTInterfaces.invoke("get_one_api_households_shopping_lists__item_id__get", {"bindings":{"item_id":{"symbol":"L1","type":"Shopping list.id"}},"id":"B2","action":"verify_absent","story":"list_recipe_membership","actor":"U1","mode":"SYMBOLIC_ONLY"});
    SBTInterfaces.invoke("add_single_recipe_ingredients_to_list_api_households_shopping_lists__item_id__recipe__recipe_id__post", {"bindings":{"item_id":{"symbol":"L1","type":"Shopping list.id"},"recipe_id":{"symbol":"R2","type":"Recipe.id"}},"id":"B3","action":"add_link","story":"list_recipe_membership","actor":"U1","mode":"SYMBOLIC_ONLY"});
    SBTInterfaces.invoke("get_one_api_households_shopping_lists__item_id__get", {"bindings":{"item_id":{"symbol":"L1","type":"Shopping list.id"}},"id":"B4","action":"verify_present","story":"list_recipe_membership","actor":"U1","mode":"SYMBOLIC_ONLY"});
});
