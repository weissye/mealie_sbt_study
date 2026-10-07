// @provengo summon rest
// @provengo summon rtv
// Deliberately large unrelated global: isolated callbacks must not capture it.
var sbtScopeSentinel=Array(1001).join('GLOBAL_SCOPE_SENTINEL:');
var svc=new RESTSession("http://127.0.0.1:9925");
function isolatedCallback(source){bp.log.info("SCOPE_STAGE: context");var cx=Packages.org.mozilla.javascript.Context.getCurrentContext();bp.log.info("SCOPE_STAGE: standard scope");var scope=cx.initStandardObjects();bp.log.info("SCOPE_STAGE: compile");var fn=cx.compileFunction(scope,"function(response){"+source+"}","isolated-scope-probe",1,null);bp.log.info("SCOPE_STAGE: compiled");return fn;}
bp.log.info("SCOPE_STAGE: model loaded");
var preparedCallbacks=[isolatedCallback("if(response.code!==200)throw new Error('Probe HTTP status');var body=JSON.parse(response.body);if(!body.info||!body.info.title)throw new Error('Contract title missing');pvg.rtv.set('sbt_scope_probe_title',body.info.title);pvg.success('SBT_SCOPE_PROBE_FIRST_PASS');"),isolatedCallback("if(response.code!==200)throw new Error('Probe HTTP status');var body=JSON.parse(response.body);if(pvg.rtv.get('sbt_scope_probe_title')!==body.info.title)throw new Error('RTV continuity failed');pvg.success('SBT_SCOPE_PROBE_NATIVE_PASS');")];
bthread("scope-probe",function(){bp.log.info("SCOPE_STAGE: bthread entered");bp.log.info("SCOPE_STAGE: before GET 0");svc.get("/openapi.json",{expectedResponseCodes:[200],callback:preparedCallbacks[0]});bp.log.info("SCOPE_STAGE: before GET 1");svc.get("/openapi.json",{expectedResponseCodes:[200],callback:preparedCallbacks[1]});sync({request:Event("SBT:ScopeProbeComplete")});});
