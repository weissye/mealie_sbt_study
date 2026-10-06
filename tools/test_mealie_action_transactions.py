"""Regression: the synthetic server must apply submitted collection replacement."""
import json,unittest
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from test_mealie_interleaved_native import NativeFixture

class ReplacementTests(unittest.TestCase):
    def test_stale_empty_replacement_removes_created_child(self):
        fixture=NativeFixture()
        base='http://127.0.0.1:'+str(fixture.server.server_port)
        def call(method,path,body=None):
            data=None if body is None else json.dumps(body).encode()
            with urlopen(Request(base+path,data=data,method=method,headers={'Content-Type':'application/json'})) as r:return json.load(r)
        try:
            parent=call('POST','/api/households/shopping/lists',{'name':'regression-parent'})
            child=call('POST','/api/households/shopping/items',{'note':'regression-child','shoppingListId':parent['id']})['createdItems'][0]
            current=call('GET','/api/households/shopping/lists/'+parent['id'])
            self.assertEqual([x['id'] for x in current['listItems']],[child['id']])
            parent['name']='regression-renamed'
            self.assertEqual(call('PUT','/api/households/shopping/lists/'+parent['id'],parent)['listItems'],[])
            with self.assertRaises(HTTPError) as failure:call('GET','/api/households/shopping/items/'+child['id'])
            self.assertEqual(failure.exception.code,404)
        finally:fixture.close()

if __name__=='__main__':unittest.main()
