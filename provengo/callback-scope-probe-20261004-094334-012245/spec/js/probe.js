// @provengo summon rest
// @provengo summon rtv
// Deliberately large unrelated global: isolated callbacks must not capture it.
var sbtScopeSentinel=Array(100001).join('GLOBAL_SCOPE_SENTINEL:');
var svc=new RESTSession("http://127.0.0.1:9925");
function isolatedCallback(source){var cx=Packages.org.mozilla.javascript.Context.getCurrentContext();var scope=cx.initStandardObjects();return cx.compileFunction(scope,"function(response){"+source+"}","isolated-scope-probe",1,null);}
bthread("scope-probe",function(){svc.get("/openapi.json",{expectedResponseCodes:[200],callback:isolatedCallback("if(response.code!==200)throw new Error('Probe HTTP status');var body=JSON.parse(response.body);if(!body.info||!body.info.title)throw new Error('Contract title missing');pvg.rtv.set('sbt_scope_probe_title',body.info.title);pvg.success('SBT_SCOPE_PROBE_FIRST_PASS');")});svc.get("/openapi.json",{expectedResponseCodes:[200],callback:isolatedCallback("if(response.code!==200)throw new Error('Probe HTTP status');var body=JSON.parse(response.body);if(pvg.rtv.get('sbt_scope_probe_title')!==body.info.title)throw new Error('RTV continuity failed');pvg.success('SBT_SCOPE_PROBE_NATIVE_PASS');")});sync({request:Event("SBT:ScopeProbeComplete")});});
