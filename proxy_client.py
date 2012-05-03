from tornado import web
from tornado import httpserver
from tornado import httpclient
from tornado import ioloop 

def handle_request(request):
    request_client = httpclient.HTTPRequest(url=request.uri, method=request.method, body=request.body or None, headers=request.headers)
    http_client = httpclient.HTTPClient()
    response = http_client.fetch(request_client)
    print(response)
    print(response.body)

http_server = httpserver.HTTPServer(handle_request)
http_server.listen(8080)
ioloop.IOLoop.instance().start()