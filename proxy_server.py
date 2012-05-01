from tornado import web
from tornado.httpserver import HTTPServer
from tornado.httpclient import HTTPClient
from tornado import ioloop 

def handle_request(request):
    http_client = HTTPClient()
    response = http_client.fetch(request)
    print(request)

http_server = HTTPServer(handle_request)
http_server.listen(8080)
ioloop.IOLoop.instance().start()