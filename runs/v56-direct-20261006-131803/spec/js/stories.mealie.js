// Generated symbolic concurrent CRUD. Callback data is runtime-only.
// @provengo summon rest
// @provengo summon rtv
bthread("verify:P1:api/foods:1", function(){
for (let stage of ["readback", "create", "read", "update", "delete"]) {
let step=sync({waitFor:EventSet("step-or-finish:P1:api/foods:1",function(e){return e.data && e.data.owner==="P1:api/foods:1" && ((e.name==="SBT:CrudStep" && e.data.stage===stage) || e.name==="SBT:WorkerFinished");})});
if(step.name==="SBT:WorkerFinished") return;
if(stage==="create" || stage==="readback") {
sbtHttp_1(step.data.values);
}
if(stage==="update") sbtHttp_2(step.data.values);
sync({request:Event("SBT:CrudVerified",{owner:"P1:api/foods:1",stage:stage,ok:true})});
}
});
bthread("crud:P1:api/foods:1", function() {
let __args={}; let __parentBindings={};
function finish(reason){ sync({request:Event("SBT:WorkerFinished",{process:1,entity:"api/foods",owner:"P1:api/foods:1",reason:reason})}); }
function verified(stage){ sync({request:Event("SBT:CrudStep",{owner:"P1:api/foods:1",process:1,entity:"api/foods",stage:stage,values:Object.assign({},__args)})});sync({waitFor:EventSet("verified:P1:api/foods:1",function(e){return e.name==="SBT:CrudVerified" && e.data.owner==="P1:api/foods:1" && e.data.stage===stage;})}); }
  let __p1_apiFoods_1_name = "name_36613";
__args["name"]=__p1_apiFoods_1_name;
sbtHttp_3(__args);
__args["itemId"]="@{sbt_P1_api_foods_1_itemId}";
sbtHttp_4(__args);
verified("readback");
verified("create");
sync({request:Event("SBT:InstanceReady",{process:1,entity:"api/foods",owner:"P1:api/foods:1",values:Object.assign({},__args)})});
sbtHttp_5(__args);
verified("read");
sbtHttp_6(__args);
verified("update");
sbtHttp_7(__args);
verified("delete");
finish("complete");
});
bthread("verify:P1:api/foods:2", function(){
for (let stage of ["readback", "create", "read", "update", "delete"]) {
let step=sync({waitFor:EventSet("step-or-finish:P1:api/foods:2",function(e){return e.data && e.data.owner==="P1:api/foods:2" && ((e.name==="SBT:CrudStep" && e.data.stage===stage) || e.name==="SBT:WorkerFinished");})});
if(step.name==="SBT:WorkerFinished") return;
if(stage==="create" || stage==="readback") {
sbtHttp_8(step.data.values);
}
if(stage==="update") sbtHttp_9(step.data.values);
sync({request:Event("SBT:CrudVerified",{owner:"P1:api/foods:2",stage:stage,ok:true})});
}
});
bthread("crud:P1:api/foods:2", function() {
let __args={}; let __parentBindings={};
function finish(reason){ sync({request:Event("SBT:WorkerFinished",{process:1,entity:"api/foods",owner:"P1:api/foods:2",reason:reason})}); }
function verified(stage){ sync({request:Event("SBT:CrudStep",{owner:"P1:api/foods:2",process:1,entity:"api/foods",stage:stage,values:Object.assign({},__args)})});sync({waitFor:EventSet("verified:P1:api/foods:2",function(e){return e.name==="SBT:CrudVerified" && e.data.owner==="P1:api/foods:2" && e.data.stage===stage;})}); }
  let __p1_apiFoods_2_name = "name_55578";
__args["name"]=__p1_apiFoods_2_name;
sbtHttp_10(__args);
__args["itemId"]="@{sbt_P1_api_foods_2_itemId}";
sbtHttp_11(__args);
verified("readback");
verified("create");
sync({request:Event("SBT:InstanceReady",{process:1,entity:"api/foods",owner:"P1:api/foods:2",values:Object.assign({},__args)})});
sbtHttp_12(__args);
verified("read");
sbtHttp_13(__args);
verified("update");
sbtHttp_14(__args);
verified("delete");
finish("complete");
});
bthread("children:P1:api/households/shopping/lists:1", function(){
let finished={}; let cleanup=false; let remaining=2;
while(remaining>0 || !cleanup){
let event=sync({waitFor:EventSet("child-finish:P1:api/households/shopping/lists:1",function(e){return e.data && ((e.name==="SBT:WorkerFinished" && ["P1:api/households/shopping/items:1", "P1:api/households/shopping/items:2"].indexOf(e.data.owner)>=0) || (e.name==="SBT:CleanupReady" && e.data.owner==="P1:api/households/shopping/lists:1"));})});
if(event.name==="SBT:CleanupReady") cleanup=true;
else if(!finished[event.data.owner]){finished[event.data.owner]=true; remaining--;}
}
sync({request:Event("SBT:ChildrenFinished",{owner:"P1:api/households/shopping/lists:1"})});
});
bthread("verify:P1:api/households/shopping/lists:1", function(){
for (let stage of ["readback", "create", "read", "delete"]) {
let step=sync({waitFor:EventSet("step-or-finish:P1:api/households/shopping/lists:1",function(e){return e.data && e.data.owner==="P1:api/households/shopping/lists:1" && ((e.name==="SBT:CrudStep" && e.data.stage===stage) || e.name==="SBT:WorkerFinished");})});
if(step.name==="SBT:WorkerFinished") return;
if(stage==="create" || stage==="readback") {
sbtHttp_15(step.data.values);
}
sync({request:Event("SBT:CrudVerified",{owner:"P1:api/households/shopping/lists:1",stage:stage,ok:true})});
}
});
bthread("crud:P1:api/households/shopping/lists:1", function() {
let __args={}; let __parentBindings={};
function finish(reason){ sync({request:Event("SBT:WorkerFinished",{process:1,entity:"api/households/shopping/lists",owner:"P1:api/households/shopping/lists:1",reason:reason})}); }
function verified(stage){ sync({request:Event("SBT:CrudStep",{owner:"P1:api/households/shopping/lists:1",process:1,entity:"api/households/shopping/lists",stage:stage,values:Object.assign({},__args)})});sync({waitFor:EventSet("verified:P1:api/households/shopping/lists:1",function(e){return e.name==="SBT:CrudVerified" && e.data.owner==="P1:api/households/shopping/lists:1" && e.data.stage===stage;})}); }
sbtHttp_16(__args);
__args["itemId"]="@{sbt_P1_api_households_shopping_lists_1_itemId}";
sbtHttp_17(__args);
verified("readback");
verified("create");
sync({request:Event("SBT:InstanceReady",{process:1,entity:"api/households/shopping/lists",owner:"P1:api/households/shopping/lists:1",values:Object.assign({},__args)})});
sbtHttp_18(__args);
verified("read");
sync({request:Event("SBT:CleanupReady",{owner:"P1:api/households/shopping/lists:1"})});
sync({waitFor:EventSet("children-done:P1:api/households/shopping/lists:1",function(e){return e.name==="SBT:ChildrenFinished" && e.data.owner==="P1:api/households/shopping/lists:1";})});
sbtHttp_19(__args);
verified("delete");
finish("complete");
});
bthread("children:P1:api/households/shopping/lists:2", function(){
let finished={}; let cleanup=false; let remaining=2;
while(remaining>0 || !cleanup){
let event=sync({waitFor:EventSet("child-finish:P1:api/households/shopping/lists:2",function(e){return e.data && ((e.name==="SBT:WorkerFinished" && ["P1:api/households/shopping/items:1", "P1:api/households/shopping/items:2"].indexOf(e.data.owner)>=0) || (e.name==="SBT:CleanupReady" && e.data.owner==="P1:api/households/shopping/lists:2"));})});
if(event.name==="SBT:CleanupReady") cleanup=true;
else if(!finished[event.data.owner]){finished[event.data.owner]=true; remaining--;}
}
sync({request:Event("SBT:ChildrenFinished",{owner:"P1:api/households/shopping/lists:2"})});
});
bthread("verify:P1:api/households/shopping/lists:2", function(){
for (let stage of ["readback", "create", "read", "delete"]) {
let step=sync({waitFor:EventSet("step-or-finish:P1:api/households/shopping/lists:2",function(e){return e.data && e.data.owner==="P1:api/households/shopping/lists:2" && ((e.name==="SBT:CrudStep" && e.data.stage===stage) || e.name==="SBT:WorkerFinished");})});
if(step.name==="SBT:WorkerFinished") return;
if(stage==="create" || stage==="readback") {
sbtHttp_20(step.data.values);
}
sync({request:Event("SBT:CrudVerified",{owner:"P1:api/households/shopping/lists:2",stage:stage,ok:true})});
}
});
bthread("crud:P1:api/households/shopping/lists:2", function() {
let __args={}; let __parentBindings={};
function finish(reason){ sync({request:Event("SBT:WorkerFinished",{process:1,entity:"api/households/shopping/lists",owner:"P1:api/households/shopping/lists:2",reason:reason})}); }
function verified(stage){ sync({request:Event("SBT:CrudStep",{owner:"P1:api/households/shopping/lists:2",process:1,entity:"api/households/shopping/lists",stage:stage,values:Object.assign({},__args)})});sync({waitFor:EventSet("verified:P1:api/households/shopping/lists:2",function(e){return e.name==="SBT:CrudVerified" && e.data.owner==="P1:api/households/shopping/lists:2" && e.data.stage===stage;})}); }
sbtHttp_21(__args);
__args["itemId"]="@{sbt_P1_api_households_shopping_lists_2_itemId}";
sbtHttp_22(__args);
verified("readback");
verified("create");
sync({request:Event("SBT:InstanceReady",{process:1,entity:"api/households/shopping/lists",owner:"P1:api/households/shopping/lists:2",values:Object.assign({},__args)})});
sbtHttp_23(__args);
verified("read");
sync({request:Event("SBT:CleanupReady",{owner:"P1:api/households/shopping/lists:2"})});
sync({waitFor:EventSet("children-done:P1:api/households/shopping/lists:2",function(e){return e.name==="SBT:ChildrenFinished" && e.data.owner==="P1:api/households/shopping/lists:2";})});
sbtHttp_24(__args);
verified("delete");
finish("complete");
});
bthread("verify:P1:api/recipes:1", function(){
for (let stage of ["readback", "create", "read", "update", "delete"]) {
let step=sync({waitFor:EventSet("step-or-finish:P1:api/recipes:1",function(e){return e.data && e.data.owner==="P1:api/recipes:1" && ((e.name==="SBT:CrudStep" && e.data.stage===stage) || e.name==="SBT:WorkerFinished");})});
if(step.name==="SBT:WorkerFinished") return;
if(stage==="create" || stage==="readback") {
sbtHttp_25(step.data.values);
}
if(stage==="update") sbtHttp_26(step.data.values);
sync({request:Event("SBT:CrudVerified",{owner:"P1:api/recipes:1",stage:stage,ok:true})});
}
});
bthread("crud:P1:api/recipes:1", function() {
let __args={}; let __parentBindings={};
function finish(reason){ sync({request:Event("SBT:WorkerFinished",{process:1,entity:"api/recipes",owner:"P1:api/recipes:1",reason:reason})}); }
function verified(stage){ sync({request:Event("SBT:CrudStep",{owner:"P1:api/recipes:1",process:1,entity:"api/recipes",stage:stage,values:Object.assign({},__args)})});sync({waitFor:EventSet("verified:P1:api/recipes:1",function(e){return e.name==="SBT:CrudVerified" && e.data.owner==="P1:api/recipes:1" && e.data.stage===stage;})}); }
  let __p1_apiRecipes_1_name = "name_34839";
__args["name"]=__p1_apiRecipes_1_name;
sbtHttp_27(__args);
__args["slug"]="@{sbt_P1_api_recipes_1_slug}";
sbtHttp_28(__args);
verified("readback");
verified("create");
sync({request:Event("SBT:InstanceReady",{process:1,entity:"api/recipes",owner:"P1:api/recipes:1",values:Object.assign({},__args)})});
sbtHttp_29(__args);
verified("read");
sbtHttp_30(__args);
verified("update");
sbtHttp_31(__args);
verified("delete");
finish("complete");
});
bthread("verify:P1:api/recipes:2", function(){
for (let stage of ["readback", "create", "read", "update", "delete"]) {
let step=sync({waitFor:EventSet("step-or-finish:P1:api/recipes:2",function(e){return e.data && e.data.owner==="P1:api/recipes:2" && ((e.name==="SBT:CrudStep" && e.data.stage===stage) || e.name==="SBT:WorkerFinished");})});
if(step.name==="SBT:WorkerFinished") return;
if(stage==="create" || stage==="readback") {
sbtHttp_32(step.data.values);
}
if(stage==="update") sbtHttp_33(step.data.values);
sync({request:Event("SBT:CrudVerified",{owner:"P1:api/recipes:2",stage:stage,ok:true})});
}
});
bthread("crud:P1:api/recipes:2", function() {
let __args={}; let __parentBindings={};
function finish(reason){ sync({request:Event("SBT:WorkerFinished",{process:1,entity:"api/recipes",owner:"P1:api/recipes:2",reason:reason})}); }
function verified(stage){ sync({request:Event("SBT:CrudStep",{owner:"P1:api/recipes:2",process:1,entity:"api/recipes",stage:stage,values:Object.assign({},__args)})});sync({waitFor:EventSet("verified:P1:api/recipes:2",function(e){return e.name==="SBT:CrudVerified" && e.data.owner==="P1:api/recipes:2" && e.data.stage===stage;})}); }
  let __p1_apiRecipes_2_name = "name_12605";
__args["name"]=__p1_apiRecipes_2_name;
sbtHttp_34(__args);
__args["slug"]="@{sbt_P1_api_recipes_2_slug}";
sbtHttp_35(__args);
verified("readback");
verified("create");
sync({request:Event("SBT:InstanceReady",{process:1,entity:"api/recipes",owner:"P1:api/recipes:2",values:Object.assign({},__args)})});
sbtHttp_36(__args);
verified("read");
sbtHttp_37(__args);
verified("update");
sbtHttp_38(__args);
verified("delete");
finish("complete");
});
bthread("verify:P1:api/units:1", function(){
for (let stage of ["readback", "create", "read", "update", "delete"]) {
let step=sync({waitFor:EventSet("step-or-finish:P1:api/units:1",function(e){return e.data && e.data.owner==="P1:api/units:1" && ((e.name==="SBT:CrudStep" && e.data.stage===stage) || e.name==="SBT:WorkerFinished");})});
if(step.name==="SBT:WorkerFinished") return;
if(stage==="create" || stage==="readback") {
sbtHttp_39(step.data.values);
}
if(stage==="update") sbtHttp_40(step.data.values);
sync({request:Event("SBT:CrudVerified",{owner:"P1:api/units:1",stage:stage,ok:true})});
}
});
bthread("crud:P1:api/units:1", function() {
let __args={}; let __parentBindings={};
function finish(reason){ sync({request:Event("SBT:WorkerFinished",{process:1,entity:"api/units",owner:"P1:api/units:1",reason:reason})}); }
function verified(stage){ sync({request:Event("SBT:CrudStep",{owner:"P1:api/units:1",process:1,entity:"api/units",stage:stage,values:Object.assign({},__args)})});sync({waitFor:EventSet("verified:P1:api/units:1",function(e){return e.name==="SBT:CrudVerified" && e.data.owner==="P1:api/units:1" && e.data.stage===stage;})}); }
  let __p1_apiUnits_1_name = "name_13598";
__args["name"]=__p1_apiUnits_1_name;
sbtHttp_41(__args);
__args["itemId"]="@{sbt_P1_api_units_1_itemId}";
sbtHttp_42(__args);
verified("readback");
verified("create");
sync({request:Event("SBT:InstanceReady",{process:1,entity:"api/units",owner:"P1:api/units:1",values:Object.assign({},__args)})});
sbtHttp_43(__args);
verified("read");
sbtHttp_44(__args);
verified("update");
sbtHttp_45(__args);
verified("delete");
finish("complete");
});
bthread("verify:P1:api/units:2", function(){
for (let stage of ["readback", "create", "read", "update", "delete"]) {
let step=sync({waitFor:EventSet("step-or-finish:P1:api/units:2",function(e){return e.data && e.data.owner==="P1:api/units:2" && ((e.name==="SBT:CrudStep" && e.data.stage===stage) || e.name==="SBT:WorkerFinished");})});
if(step.name==="SBT:WorkerFinished") return;
if(stage==="create" || stage==="readback") {
sbtHttp_46(step.data.values);
}
if(stage==="update") sbtHttp_47(step.data.values);
sync({request:Event("SBT:CrudVerified",{owner:"P1:api/units:2",stage:stage,ok:true})});
}
});
bthread("crud:P1:api/units:2", function() {
let __args={}; let __parentBindings={};
function finish(reason){ sync({request:Event("SBT:WorkerFinished",{process:1,entity:"api/units",owner:"P1:api/units:2",reason:reason})}); }
function verified(stage){ sync({request:Event("SBT:CrudStep",{owner:"P1:api/units:2",process:1,entity:"api/units",stage:stage,values:Object.assign({},__args)})});sync({waitFor:EventSet("verified:P1:api/units:2",function(e){return e.name==="SBT:CrudVerified" && e.data.owner==="P1:api/units:2" && e.data.stage===stage;})}); }
  let __p1_apiUnits_2_name = "name_24297";
__args["name"]=__p1_apiUnits_2_name;
sbtHttp_48(__args);
__args["itemId"]="@{sbt_P1_api_units_2_itemId}";
sbtHttp_49(__args);
verified("readback");
verified("create");
sync({request:Event("SBT:InstanceReady",{process:1,entity:"api/units",owner:"P1:api/units:2",values:Object.assign({},__args)})});
sbtHttp_50(__args);
verified("read");
sbtHttp_51(__args);
verified("update");
sbtHttp_52(__args);
verified("delete");
finish("complete");
});
bthread("bind:P1:api/households/shopping/items:1", function(){
let available={}; let candidates=[]; let required=["api/households/shopping/lists"];
while(true){
let first=available[required[0]]||[];
candidates=first.filter(function(anchor){return required.every(function(type){
return (available[type]||[]).some(function(parent){return anchor.values.realm===undefined || parent.values.realm===undefined || parent.values.realm===anchor.values.realm;});});});
if(candidates.length) break;
let ready=sync({waitFor:EventSet("any-parent:P1:api/households/shopping/items:1",function(e){return e.name==="SBT:InstanceReady" && e.data && e.data.process===1 && required.indexOf(e.data.entity)>=0;})});
if(!available[ready.data.entity]) available[ready.data.entity]=[];
available[ready.data.entity].push({owner:ready.data.owner,values:ready.data.values});
}
let parents={};
let options=candidates.map(function(parent,index){return Event("SBT:BindParent",{child:"P1:api/households/shopping/items:1",type:required[0],index:index});});
let chosen=sync({request:options});
let anchor=candidates[chosen.data.index]; parents[required[0]]=anchor.values;
for(let i=1;i<required.length;i++){
let type=required[i]; let matches=available[type].filter(function(parent){return anchor.values.realm===undefined || parent.values.realm===undefined || parent.values.realm===anchor.values.realm;});
let choices=matches.map(function(parent,index){return Event("SBT:BindParent",{child:"P1:api/households/shopping/items:1",type:type,index:index});});
let picked=sync({request:choices}); parents[type]=matches[picked.data.index].values;
}
sync({request:Event("SBT:ParentsBound",{owner:"P1:api/households/shopping/items:1",parents:parents})});
});
bthread("verify:P1:api/households/shopping/items:1", function(){
for (let stage of ["readback", "create", "read", "update", "delete"]) {
let step=sync({waitFor:EventSet("step-or-finish:P1:api/households/shopping/items:1",function(e){return e.data && e.data.owner==="P1:api/households/shopping/items:1" && ((e.name==="SBT:CrudStep" && e.data.stage===stage) || e.name==="SBT:WorkerFinished");})});
if(step.name==="SBT:WorkerFinished") return;
if(stage==="create" || stage==="readback") {
sbtHttp_53(step.data.values);
}
if(stage==="update") sbtHttp_54(step.data.values);
sync({request:Event("SBT:CrudVerified",{owner:"P1:api/households/shopping/items:1",stage:stage,ok:true})});
}
});
bthread("crud:P1:api/households/shopping/items:1", function() {
let __args={}; let __parentBindings={};
function finish(reason){ sync({request:Event("SBT:WorkerFinished",{process:1,entity:"api/households/shopping/items",owner:"P1:api/households/shopping/items:1",reason:reason})}); }
function verified(stage){ sync({request:Event("SBT:CrudStep",{owner:"P1:api/households/shopping/items:1",process:1,entity:"api/households/shopping/items",stage:stage,values:Object.assign({},__args)})});sync({waitFor:EventSet("verified:P1:api/households/shopping/items:1",function(e){return e.name==="SBT:CrudVerified" && e.data.owner==="P1:api/households/shopping/items:1" && e.data.stage===stage;})}); }
let bound=sync({waitFor:EventSet("bound:P1:api/households/shopping/items:1",function(e){return e.name==="SBT:ParentsBound" && e.data.owner==="P1:api/households/shopping/items:1";})});
__parentBindings=bound.data.parents;
{
if(__args.realm===undefined && __parentBindings["api/households/shopping/lists"].realm!==undefined) __args.realm=__parentBindings["api/households/shopping/lists"].realm;
__args["shoppingListId"]=__parentBindings["api/households/shopping/lists"]["itemId"];
}
__args["shoppingListId"]=__args["shoppingListId"];
sbtHttp_55(__args);
__args["itemId"]="@{sbt_P1_api_households_shopping_items_1_itemId}";
sbtHttp_56(__args);
verified("readback");
verified("create");
sync({request:Event("SBT:InstanceReady",{process:1,entity:"api/households/shopping/items",owner:"P1:api/households/shopping/items:1",values:Object.assign({},__args)})});
sbtHttp_57(__args);
verified("read");
sbtHttp_58(__args);
verified("update");
sbtHttp_59(__args);
verified("delete");
finish("complete");
});
bthread("bind:P1:api/households/shopping/items:2", function(){
let available={}; let candidates=[]; let required=["api/households/shopping/lists"];
while(true){
let first=available[required[0]]||[];
candidates=first.filter(function(anchor){return required.every(function(type){
return (available[type]||[]).some(function(parent){return anchor.values.realm===undefined || parent.values.realm===undefined || parent.values.realm===anchor.values.realm;});});});
if(candidates.length) break;
let ready=sync({waitFor:EventSet("any-parent:P1:api/households/shopping/items:2",function(e){return e.name==="SBT:InstanceReady" && e.data && e.data.process===1 && required.indexOf(e.data.entity)>=0;})});
if(!available[ready.data.entity]) available[ready.data.entity]=[];
available[ready.data.entity].push({owner:ready.data.owner,values:ready.data.values});
}
let parents={};
let options=candidates.map(function(parent,index){return Event("SBT:BindParent",{child:"P1:api/households/shopping/items:2",type:required[0],index:index});});
let chosen=sync({request:options});
let anchor=candidates[chosen.data.index]; parents[required[0]]=anchor.values;
for(let i=1;i<required.length;i++){
let type=required[i]; let matches=available[type].filter(function(parent){return anchor.values.realm===undefined || parent.values.realm===undefined || parent.values.realm===anchor.values.realm;});
let choices=matches.map(function(parent,index){return Event("SBT:BindParent",{child:"P1:api/households/shopping/items:2",type:type,index:index});});
let picked=sync({request:choices}); parents[type]=matches[picked.data.index].values;
}
sync({request:Event("SBT:ParentsBound",{owner:"P1:api/households/shopping/items:2",parents:parents})});
});
bthread("verify:P1:api/households/shopping/items:2", function(){
for (let stage of ["readback", "create", "read", "update", "delete"]) {
let step=sync({waitFor:EventSet("step-or-finish:P1:api/households/shopping/items:2",function(e){return e.data && e.data.owner==="P1:api/households/shopping/items:2" && ((e.name==="SBT:CrudStep" && e.data.stage===stage) || e.name==="SBT:WorkerFinished");})});
if(step.name==="SBT:WorkerFinished") return;
if(stage==="create" || stage==="readback") {
sbtHttp_60(step.data.values);
}
if(stage==="update") sbtHttp_61(step.data.values);
sync({request:Event("SBT:CrudVerified",{owner:"P1:api/households/shopping/items:2",stage:stage,ok:true})});
}
});
bthread("crud:P1:api/households/shopping/items:2", function() {
let __args={}; let __parentBindings={};
function finish(reason){ sync({request:Event("SBT:WorkerFinished",{process:1,entity:"api/households/shopping/items",owner:"P1:api/households/shopping/items:2",reason:reason})}); }
function verified(stage){ sync({request:Event("SBT:CrudStep",{owner:"P1:api/households/shopping/items:2",process:1,entity:"api/households/shopping/items",stage:stage,values:Object.assign({},__args)})});sync({waitFor:EventSet("verified:P1:api/households/shopping/items:2",function(e){return e.name==="SBT:CrudVerified" && e.data.owner==="P1:api/households/shopping/items:2" && e.data.stage===stage;})}); }
let bound=sync({waitFor:EventSet("bound:P1:api/households/shopping/items:2",function(e){return e.name==="SBT:ParentsBound" && e.data.owner==="P1:api/households/shopping/items:2";})});
__parentBindings=bound.data.parents;
{
if(__args.realm===undefined && __parentBindings["api/households/shopping/lists"].realm!==undefined) __args.realm=__parentBindings["api/households/shopping/lists"].realm;
__args["shoppingListId"]=__parentBindings["api/households/shopping/lists"]["itemId"];
}
__args["shoppingListId"]=__args["shoppingListId"];
sbtHttp_62(__args);
__args["itemId"]="@{sbt_P1_api_households_shopping_items_2_itemId}";
sbtHttp_63(__args);
verified("readback");
verified("create");
sync({request:Event("SBT:InstanceReady",{process:1,entity:"api/households/shopping/items",owner:"P1:api/households/shopping/items:2",values:Object.assign({},__args)})});
sbtHttp_64(__args);
verified("read");
sbtHttp_65(__args);
verified("update");
sbtHttp_66(__args);
verified("delete");
finish("complete");
});
