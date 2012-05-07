from tornado import web
from tornado import httpserver
from tornado.httpclient import HTTPRequest
from tornado import ioloop 
from tornado.curl_httpclient import CurlAsyncHTTPClient

class ProxyServer(web.RequestHandler):
    def response_client(self, response):
        self.write(response.body)
        self.finish()

    @web.asynchronous
    def get(self):
        request_client = HTTPRequest(url = self.request.uri, method = self.request.method, body = self.request.body or None, headers = self.request.headers)
        http_client = CurlAsyncHTTPClient()
        response = http_client.fetch(request_client, self.response_client)

app = web.Application([(r'.*', ProxyServer),])
http_server = httpserver.HTTPServer(app)
http_server.listen(8888)
ioloop.IOLoop.instance().start()