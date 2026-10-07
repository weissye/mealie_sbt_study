import json
from http.server import BaseHTTPRequestHandler

class Fixture(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def body(self):
        data = self.rfile.read(int(self.headers.get('Content-Length', '0')))
        return json.loads(data or b'{}')

    def reply(self, status, body):
        payload = body.encode() if isinstance(body, str) else json.dumps(body).encode()
        self.server.receipts.append({'method': self.command, 'path': self.path, 'status': status, 'state': dict(self.server.resource) if self.server.resource else None})
        self.send_response(status)
        self.send_header('Content-Type', 'text/plain' if isinstance(body, str) else 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        body = self.body()
        if self.path == '/resources':
            self.server.resource = {'id': 'fixture-1', 'name': body['name']}
            self.reply(201, self.server.resource)
        elif self.path == '/resources/fixture-1/action':
            if self.server.mode == 'control':
                self.reply(200, self.server.resource)
            else:
                if self.server.mode == 'changed':
                    self.server.resource['name'] = 'injected-change'
                self.reply(500, 'Internal Server Error')
        else:
            self.reply(404, {})

    def do_PATCH(self):
        body = self.body()
        if self.path == '/resources/fixture-1' and self.server.resource:
            self.server.resource.update(body)
            self.reply(200, self.server.resource)
        else:
            self.reply(404, {})

    def do_GET(self):
        if self.path == '/resources/fixture-1' and self.server.resource:
            self.reply(200, self.server.resource)
        else:
            self.reply(404, {})

