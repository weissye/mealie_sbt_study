// @provengo summon rest
// @provengo summon rtv
// @provengo summon context
var diagSvc=new RESTSession("http://127.0.0.1:53172","auth-diagnostic",{});
function diagnosticLogin(){diagSvc.post("/api/auth/token",{headers:{"Content-Type":"application/x-www-form-urlencoded"},body:"grant_type=password&username=@{encodeURIComponent(getEnv('SBT_REL_USERNAME'))}&password=@{encodeURIComponent(getEnv('SBT_REL_PASSWORD'))}",expectedResponseCodes:[200],callback:function(response){var value=JSON.parse(response.body);if(!value.access_token){pvg.fail("Authentication token missing");return;}pvg.success("SBT_AUTH_DIAGNOSTIC_TOKEN_PRESENT");}});}
