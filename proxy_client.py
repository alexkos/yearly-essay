from tornado import web
from tornado import httpserver
from tornado.httpclient import HTTPRequest
from tornado import ioloop 
from tornado.curl_httpclient import CurlAsyncHTTPClient

def handle_request(request):
    def response_client():
        print response
    request_client = HTTPRequest(url=request.uri, method=request.method, body=request.body or None, \
        headers=request.headers, proxy_host = '127.0.0.1', proxy_port = 8888)
    http_client = CurlAsyncHTTPClient()
    response = http_client.fetch(request_client,response_client)

http_server = httpserver.HTTPServer(handle_request)
http_server.listen(8080)
ioloop.IOLoop.instance().start()

