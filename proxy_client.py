import logging
from tornado import options
from tornado import web
from tornado import httpserver
from tornado.httpclient import HTTPRequest
from tornado import ioloop 
from tornado.curl_httpclient import CurlAsyncHTTPClient

class ProxyClient(web.RequestHandler):
    def response_client(self, response):
        self.write(response.body)
        self.finish()

    @web.asynchronous
    def get(self):
        request_client = HTTPRequest(url = self.request.uri, method = self.request.method, body = self.request.body or None, \
            headers = self.request.headers, proxy_host = '127.0.0.1', proxy_port = 8888)
        http_client = CurlAsyncHTTPClient()
        response = http_client.fetch(request_client, self.response_client)

options.parse_command_line()
logging.info('Client server started @ 127.0.0.1:8080 -> proxy server: 127.0.0.0:8888')
app = web.Application([(r'.*', ProxyClient),])
http_server = httpserver.HTTPServer(app)
http_server.listen(8080)
ioloop.IOLoop.instance().start()