// Local HTTP fixture for native Provengo callback regression tests.
// This models API responses; it is not a live Mealie server.
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=process.argv[2],seed=1,fault=process.env.NATIVE_MOCK_FAULT||'',missingMode='';
const model=JSON.parse(fs.readFileSync(path.join(root,'relationship_scenario_plan.json'),'utf8'));
const expandedViews=model.tasks.some(t=>t.kind==='dependency_transfer'||(t.kind==='shared_update'&&t.referrers.some(r=>r.object_path)));
const actors=[],rtv={},objects={},requests=[],selected=[],failures=[];
let callbackBytes=0,counter=0,random=seed,activeRequests=0,maximumActive=0,corrupt=false,currentTask=null,sharedChanged=false;
function uuid(){return '00000000-0000-4000-8000-'+String(++counter).padStart(12,'0');}
function pick(n){random=(Math.imul(random,1664525)+1013904223)>>>0;return random%n;}
function interpolate(value){return value;}
const createOps={};
for(const t of model.tasks.filter(t=>t.kind==='create'))createOps[t.operation.split(' ')[1]]=t.resource;
const fakeScope={id:'11111111-1111-4111-8111-111111111111',groupId:'22222222-2222-4222-8222-222222222222',householdId:'33333333-3333-4333-8333-333333333333'};
function serve(method,url,options){
  url=interpolate(url);let body=options.body?interpolate(options.body):null;
  activeRequests++;maximumActive=Math.max(maximumActive,activeRequests);
  requests.push({method,url,task:currentTask});let result,status=method==='post'?201:200;
  try{
    const semantic=require('./semantic_http_fixture')(model,objects,uuid,fault,method,url,body);
    if(semantic){result=semantic.result;status=semantic.status;}
    else if(url.includes('/auth/token')){result={access_token:'FAKE_TOKEN',token_type:'bearer'};status=200;}
    else if(url==='/api/users/self')result=fakeScope;
    else if(url==='/api/groups/self')result={id:fault==='scope'?uuid():fakeScope.groupId};
    else if(url==='/api/households/self')result={id:fakeScope.householdId,groupId:fakeScope.groupId};
    else if(method==='post'&&createOps[url]){
      const data=JSON.parse(body),resource=createOps[url];const id=uuid(),slug='owned-'+counter;
      result={...data,id,slug,groupId:fakeScope.groupId,userId:fakeScope.id,householdId:fakeScope.householdId};
      if(resource==='api/recipes')Object.assign(result,{recipeIngredient:[],recipeCategory:[],tags:[]});
      if(resource==='api/households/shopping/lists')Object.assign(result,{listItems:[],recipeReferences:[]});
      if(resource==='api/households/shopping/items')Object.assign(result,{food:null,foodId:null,unit:fault==='projection-null'?17:null,unitId:null,referencedRecipe:null,recipeReferences:model.semantic_program?[]:[{id:uuid(),shoppingListItemId:id,recipeId:'44444444-4444-4444-8444-444444444444',recipeQuantity:2,recipeScale:1}]});
      const itemUrl=url+'/'+(resource==='api/recipes'?slug:id);objects[itemUrl]=result;
      if(resource==='api/recipes')result=slug;
      else if(resource==='api/households/shopping/items')result={createdItems:[result],updatedItems:[],deletedItems:[]};
      if(fault==='ambiguous-create'&&resource==='api/households/shopping/items')result.createdItems.push({...result.createdItems[0],id:uuid()});
    }else if(method==='get'&&objects[url]){result=objects[url];
      if(model.tasks.some(t=>t.rule?.stale_snapshot)&&result.recipeReferences){
        result=JSON.parse(JSON.stringify(result));
        result.recipeReferences.forEach(ref=>{const recipe=Object.values(objects).find(x=>x.recipeIngredient&&x.id===ref.recipeId);if(recipe)ref.recipe={id:recipe.id,name:recipe.name,description:recipe.description||'',dateUpdated:recipe.dateUpdated||'before',updatedAt:recipe.updatedAt||'before'};});
      }
      if(expandedViews&&fault!=='embedded-stale'){
        result=JSON.parse(JSON.stringify(result));
        function hydrate(node){if(!node||typeof node!=='object')return;for(const field of ['food','unit']){if(node[field]?.id){const family=field==='food'?'foods':'units',current=objects['/api/'+family+'/'+node[field].id];if(current)node[field]=JSON.parse(JSON.stringify(current));}}for(const value of Object.values(node))if(value&&typeof value==='object')hydrate(value);}
        hydrate(result);
      }
      if(fault==='shared-reference-changed'&&sharedChanged&&result.recipeIngredient?.some(x=>x.food)){result=JSON.parse(JSON.stringify(result));result.recipeIngredient.forEach(x=>{if(x.food)x.food.id=uuid();});}
      if(fault==='legal-target-id'&&currentTask?.endsWith(':legal-reverse')&&url!==Object.keys(objects).find(k=>objects[k].id===JSON.parse(rtv[model.instance_metadata[model.tasks.find(t=>t.id===currentTask).source_instance].snapshot_variable]).id))result={...result,id:uuid()};
      if(fault==='route-id'&&url.startsWith('/api/foods/'))result={...result,id:uuid()};
      if(fault==='readback'&&corrupt&&result.recipeIngredient?.some(x=>x.food)){
        result=JSON.parse(JSON.stringify(result));result.recipeIngredient.forEach(x=>{if(x.food)x.food.id=uuid();});corrupt=false;
      }
    }else if((method==='put'||method==='patch')&&objects[url]){const data=JSON.parse(body);
      const sharedUpdate=(url.startsWith('/api/foods/')||url.startsWith('/api/units/'))&&data.name?.includes('-updated');
      if(sharedUpdate){sharedChanged=true;if(fault==='shared-update-ignored')data.name=objects[url].name;}
      if(url.startsWith('/api/households/shopping/items/')){
        // Model an API whose scalar foreign keys determine hydrated relationship objects.
        for(const field of ['food','unit']){
          const family=field==='food'?'foods':'units',key=data[field+'Id'];
          data[field]=key?objects['/api/'+family+'/'+key]:null;
          assert(!key||data[field], 'Unknown foreign key');
        }
        // The inherited field is ignored; item-to-recipe associations are separate records.
        data.referencedRecipe=null;
        for(const old of objects[url].recipeReferences||[]){const retained=(data.recipeReferences||[]).find(x=>x.recipeId===old.recipeId);assert(retained&&retained.id===old.id,'Existing association identity was lost');assert.strictEqual(retained.recipeQuantity,old.recipeQuantity);}
        data.recipeReferences=(data.recipeReferences||[]).map(x=>({...x,id:x.id||uuid(),shoppingListItemId:objects[url].id}));
        if(fault==='association-readback'&&data.recipeReferences.length>1)data.recipeReferences[1].recipeId=uuid();
      }
      let cycle=false;
      if(url.startsWith('/api/recipes/')){
        if(model.tasks.some(t=>t.kind==='reference_lifecycle'))for(const ingredient of data.recipeIngredient||[]){ingredient.display=[ingredient.quantity,ingredient.unit?.name,ingredient.food?.name,ingredient.note].filter(v=>v!==undefined&&v!==null&&v!=='').join(' ');}
        const recipes=Object.values(objects).filter(x=>x.recipeIngredient),source=objects[url].id;
        function reaches(id,seen){if(id===source)return true;if(seen.has(id))return false;seen.add(id);const item=recipes.find(x=>x.id===id);return (item?.recipeIngredient||[]).some(x=>x.referencedRecipe&&reaches(x.referencedRecipe.id,seen));}
        cycle=(data.recipeIngredient||[]).some(x=>x.referencedRecipe&&reaches(x.referencedRecipe.id,new Set()));
      }
      if(fault==='alternate-path-ignored'&&currentTask?.endsWith(':reject-remaining-path'))cycle=false;
      if(cycle&&fault!=='cycle-accepted'){
        status=fault==='cycle-500'?500:400;result={detail:'Recursive Recipe Link Error'};
        if(fault==='cycle-mutates-on-reject')objects[url].description='PARTIAL_WRITE_DESPITE_REJECTION';
        if(fault==='cycle-target-mutates-on-reject'){const target=(data.recipeIngredient||[]).find(x=>x.referencedRecipe)?.referencedRecipe.id;const member=Object.values(objects).find(x=>x.id===target);assert(member);member.description='TARGET_WRITE_DESPITE_REJECTION';}
      }else if(fault==='legal-rejected'&&currentTask?.endsWith(':legal-reverse')){status=400;result={detail:'Incorrect rejection of acyclic link'};}
      else if((fault==='unlink-ignored'&&currentTask?.endsWith(':unlink'))||(fault==='alternate-unlink-ignored'&&currentTask?.endsWith(':remove-left'))){result=objects[url];}
      else if(data.description?.includes('-stale-write')&&model.tasks.some(t=>t.rule?.stale_snapshot&&t.rule.mode==='delete')&&fault!=='stale-accepted'){status=422;result={detail:'Removed dependency'};if(fault==='stale-partial')objects[url].description=data.description;if(fault==='stale-other-source')for(const other of Object.values(objects))if(other.recipeIngredient&&other.id!==objects[url].id)other.recipeIngredient[0].quantity=999;}
      else{if(data.description?.includes('-post-delete-')&&fault==='reference-followup-ignored')data.description=objects[url].description;
        if(data.description?.includes('-post-delete-')&&fault==='reference-rebind-ignored'&&data.recipeIngredient?.some(x=>x.food||x.unit))data.recipeIngredient=objects[url].recipeIngredient;
        objects[url]={...objects[url],...data};result=objects[url];corrupt=fault==='readback';
        if(model.tasks.some(t=>t.kind==='dependency_transfer')&&Object.values(objects).some(x=>x.name?.includes('-old-before-transfer'))){
          if(fault==='transfer-quantity'&&result.recipeIngredient)result.recipeIngredient[0].quantity=999;
          if(fault==='transfer-unrelated-target'&&!result.recipeIngredient)for(const other of Object.values(objects))if(other.id!==result.id&&other.name&&!other.recipeIngredient&&!other.recipeReferences)other.name='UNRELATED_TARGET';
        }
        if(data.description?.includes('-stale-write')){
          result.dateUpdated='after';result.updatedAt='after';
          if(fault==='stale-list-quantity')for(const list of Object.values(objects))if(list.recipeReferences?.length)list.recipeReferences[0].recipeQuantity=999;
          if(fault==='stale-view-name')result.name='UNEXPECTED_NAME';
        }
        if(fault==='identity-view'&&url.startsWith('/api/households/shopping/items/')&&data.foodId)result.foodId=uuid();
      }
    }
    else if(method==='delete'&&objects[url]){result=objects[url];status=200;
      const reference=model.tasks.find(t=>t.kind==='reference_lifecycle');
      

      if(reference&&(fault==='reference-reject'||fault==='reference-reject-partial')){status=409;if(fault==='reference-reject-partial')for(const object of Object.values(objects))if(object.recipeIngredient)object.recipeIngredient[0].quantity=999;}else if(fault!=='delete-ignored'){
        delete objects[url];
        if(reference&&fault!=='reference-dangling'){
          const field=reference.rule.field_path.split('.').pop();
          for(const object of Object.values(objects))for(const ingredient of object.recipeIngredient||[]){if(ingredient[field]?.id===result.id)ingredient[field]=null;}
          if(fault==='reference-unrelated')for(const object of Object.values(objects))if(object.recipeIngredient?.length)object.recipeIngredient[0].quantity=999;
        }
        if(model.tasks.some(t=>t.kind==='attached_delete')&&fault!=='delete-dangling'){
          const field=url.startsWith('/api/organizers/tags/')?'tags':url.startsWith('/api/organizers/categories/')?'recipeCategory':null;
          if(field)for(const object of Object.values(objects))if(Array.isArray(object[field]))object[field]=object[field].filter(x=>x.id!==result.id);
        }
      }
      if(fault==='delete-unrelated-links'){for(const object of Object.values(objects))if(object.recipeIngredient)object.recipeIngredient=[];}
      if(fault==='delete-cascades-source'){const recipe=Object.keys(objects).find(k=>k.startsWith('/api/recipes/'));if(recipe)delete objects[recipe];}
    }
    else if(method==='get'){status=404;result={detail:'Not found'};}
    else if(method==='post'&&url.includes('/recipe/')){const offset=url.lastIndexOf('/recipe/'),source=url.slice(0,offset),target=url.slice(offset+8);result=objects[source];assert(result);result.recipeReferences.push({recipeId:target});status=200;}
    else throw new Error('Unrecognized mock HTTP '+method+' '+url);
    return {status,result};
  }finally{activeRequests--;}
}

const http=require('http');
http.createServer((req,res)=>{let body='';req.on('data',d=>body+=d);req.on('end',()=>{try{const value=serve(req.method.toLowerCase(),req.url,{body});res.writeHead(value.status,{'Content-Type':'application/json'});res.end(JSON.stringify(value.result));}catch(error){res.writeHead(500);res.end(JSON.stringify({error:String(error)}));}});}).listen(Number(process.env.NATIVE_MOCK_PORT||9925),'127.0.0.1',()=>console.log('READY'));
