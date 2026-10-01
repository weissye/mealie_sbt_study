// Offline symbolic model. No REST library or HTTP executor is loaded.
bthread("recipe_description", function () {
    request(Event("SBT:Step", {"id":"A1","action":"capture_recipe_description","method":"GET","path":"/api/recipes/{slug}","bindings":{"slug":{"symbol":"R2","type":"Recipe.slug"}},"story":"recipe_description","actor":"U1","mode":"SYMBOLIC_ONLY"}));
    request(Event("SBT:Step", {"id":"A2","action":"set_owned_recipe_description","method":"PUT","path":"/api/recipes/{slug}","bindings":{"slug":{"symbol":"R2","type":"Recipe.slug"}},"story":"recipe_description","actor":"U1","mode":"SYMBOLIC_ONLY"}));
    request(Event("SBT:Step", {"id":"A3","action":"verify_updated_recipe_description","method":"GET","path":"/api/recipes/{slug}","bindings":{"slug":{"symbol":"R2","type":"Recipe.slug"}},"story":"recipe_description","actor":"U1","mode":"SYMBOLIC_ONLY"}));
    request(Event("SBT:Step", {"id":"A4","action":"restore_captured_recipe_description","method":"PUT","path":"/api/recipes/{slug}","bindings":{"slug":{"symbol":"R2","type":"Recipe.slug"}},"story":"recipe_description","actor":"U1","mode":"SYMBOLIC_ONLY"}));
});
bthread("list_recipe_membership", function () {
    request(Event("SBT:Step", {"id":"B1","action":"unlink_owned_recipe_from_list","method":"POST","path":"/api/households/shopping/lists/{item_id}/recipe/{recipe_id}/delete","bindings":{"item_id":{"symbol":"L1","type":"Shopping list.id"},"recipe_id":{"symbol":"R2","type":"Recipe.id"}},"story":"list_recipe_membership","actor":"U1","mode":"SYMBOLIC_ONLY"}));
    request(Event("SBT:Step", {"id":"B2","action":"verify_recipe_link_absent","method":"GET","path":"/api/households/shopping/lists/{item_id}","bindings":{"item_id":{"symbol":"L1","type":"Shopping list.id"}},"story":"list_recipe_membership","actor":"U1","mode":"SYMBOLIC_ONLY"}));
    request(Event("SBT:Step", {"id":"B3","action":"relink_owned_recipe_to_list","method":"POST","path":"/api/households/shopping/lists/{item_id}/recipe/{recipe_id}","bindings":{"item_id":{"symbol":"L1","type":"Shopping list.id"},"recipe_id":{"symbol":"R2","type":"Recipe.id"}},"story":"list_recipe_membership","actor":"U1","mode":"SYMBOLIC_ONLY"}));
    request(Event("SBT:Step", {"id":"B4","action":"verify_recipe_link_present","method":"GET","path":"/api/households/shopping/lists/{item_id}","bindings":{"item_id":{"symbol":"L1","type":"Shopping list.id"}},"story":"list_recipe_membership","actor":"U1","mode":"SYMBOLIC_ONLY"}));
});
