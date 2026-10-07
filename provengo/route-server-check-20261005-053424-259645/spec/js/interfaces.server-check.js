//@provengo summon rest
const checkSvc=new RESTSession("http://127.0.0.1:9925","route-server-check");

function auditCallback(source){
var hydrate="if(typeof Packages!=='undefined'){Packages.org.mozilla.javascript.Context.getCurrentContext().initStandardObjects(Packages.org.mozilla.javascript.ScriptableObject.getTopLevelScope(this));}";
source=hydrate+source;
if(typeof Packages!=='undefined'){
var scope=new Packages.org.mozilla.javascript.NativeObject();
(new Packages.org.mozilla.javascript.ClassCache()).associate(scope);
return Packages.org.mozilla.javascript.Context.getCurrentContext().compileFunction(scope,"function(response,arguments){"+source+"}","read-only-audit-callback",1,null);
}
return new Function('response',source);
}

function checkContract(){checkSvc.get("/openapi.json",{expectedResponseCodes:[200],callback:auditCallback("var body=JSON.parse(response.body);pvg.rtv.set('route_server_contract',JSON.stringify({code:response.code,version:body.info.version}));")});}
