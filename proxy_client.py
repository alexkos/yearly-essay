from tornado import web
from tornado import httpserver
from tornado import httpclient
from tornado import ioloop 

def handle_request(request):
    request_client = httpclient.HTTPRequest(url=request.uri, method=request.method, body=request.body or None, \
        headers=request.headers, proxy_host = '127.0.0.1', proxy_port = '8888')
    http_client = httpclient.HTTPClient()
    response = http_client.fetch(request_client)

http_server = httpserver.HTTPServer(handle_request)
http_server.listen(8080)
ioloop.IOLoop.instance().start()
