from tornado import httpserver
from tornado import ioloop 

def handle_request(request):
    http_client = httpclient.HTTPClient()

http_server = httpserver.HTTPServer(handle_request)
http_server.listen(8888)
ioloop.IOLoop.instance().start()