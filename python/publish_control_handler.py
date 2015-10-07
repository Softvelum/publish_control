#!/usr/bin/env python

import argparse
import json
import SimpleHTTPServer
import SocketServer
import ssl

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int)
parser.add_argument('--https', action='store_true', default=False)
args = parser.parse_args()

port = 8085
if args.port != None:
	port = args.port

not_found = '<html><head><title>Not found</title></head><body>Not found</body></html>'

ppp_handler_calls = 0

class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    __posts = []

    def send_404(self):
        self.send_response(404)
        self.send_header('Content-Length', len(not_found))
        self.end_headers()
        self.wfile.write(not_found)

    def do_GET(self):

        if self.path == '/pay_per_publish':
            global ppp_handler_calls
            print('ppp_handler_calls=%s' % ppp_handler_calls)
            response_body = str(ppp_handler_calls)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(response_body))
            self.end_headers()
            self.wfile.write(response_body)
        else:
            self.send_404()

    def do_POST(self):
        global ppp_handler_calls
        if self.path == '/pay_per_publish/reset':
            ppp_handler_calls = 0
            self.send_response(200)
            self.end_headers()
        elif self.path == '/pay_per_publish':
            request = self.rfile.read(int(self.headers['Content-Length']))
            pay_per_publish_request_json = json.loads(request)

            result = []

            for auth in pay_per_publish_request_json['PublishAuthRequest']:
                seq = auth['seq']
                id = auth['id']
                if id.startswith('ID_'):
                    result.append({"seq": seq, "status":"success"})
                else:
                    result.append({"seq": seq, "status":"fail"})

            ppp_handler_calls+=1

            result = {"PublishAuthResponse": result}
            response_body = json.dumps(result)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response_body))
            self.end_headers()
            self.wfile.write(response_body)
        else:
            print('FAIL')
            fail_500 = '500'
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(fail_500))
            self.end_headers()
            self.wfile.write(fail_500)

SocketServer.TCPServer.allow_reuse_address = True
httpd = SocketServer.TCPServer(("", port), HTTPHandler)

if args.https:
    httpd.socket = ssl.wrap_socket(
                      httpd.socket,
                      keyfile='./test/ssl_cert_no_pass/server_no_passphrase.key',
                      certfile='./test/ssl_cert_no_pass/server.crt',
                      server_side=True)

try:
    httpd.serve_forever()
except KeyboardInterrupt, e:
    pass
finally:
    httpd.socket.close()
