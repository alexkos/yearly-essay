from tornado import web
from tornado import httpserver
from tornado.httpclient import HTTPRequest
from tornado import ioloop 
from tornado.curl_httpclient import CurlAsyncHTTPClient

class ProxyClient(web.RequestHandler):
    def get(self):
        def response_client(response):
            print '!!!!!!!!!!!!'
        request_client = HTTPRequest(url = self.request.uri, method = self.request.method, body = self.request.body or None, \
            headers = self.request.headers, proxy_host = '127.0.0.1', proxy_port = 8888)
        http_client = CurlAsyncHTTPClient()
        response = http_client.fetch(request_client,response_client)

app = web.Application([(r'.*', Proxy),])
http_server = httpserver.HTTPServer(app)
http_server.listen(8080)
ioloop.IOLoop.instance().start()