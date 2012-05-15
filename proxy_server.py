import os
import base64
import logging
import M2Crypto
from Crypto.Cipher import AES
from tornado import options
from tornado import web
from tornado import httpserver
from tornado.httpclient import HTTPRequest
from tornado import ioloop 
from tornado.curl_httpclient import CurlAsyncHTTPClient

class ProxyServer(web.RequestHandler):
    def encrypt(self, cipher, enc_body):
        padding = '{'
        pad = lambda s: s + (blocksize - len(s) % blocksize) * padding
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
        encoded = EncodeAES(cipher, enc_body)
        return encoded

    def response_client(self, response):
        #ReadProxy_server = M2Crypto.RSA.load_key ('proxy_server-private.key')
        #key_aes = ReadProxy_server.private_decrypt ('getting encrypt key', M2Crypto.RSA.pkcs1_oaep_padding)
        self.write(self.encrypt(key_aes, response.body))
        self.finish()

    @web.asynchronous
    def get(self):
        request_client = HTTPRequest(url = self.request.uri, method = self.request.method, body = self.request.body or None, \
            headers = self.request.headers)
        http_client = CurlAsyncHTTPClient()
        response = http_client.fetch(request_client, self.response_client)

#M2Crypto.Rand.rand_seed(os.urandom(1024))
#proxy_server = M2Crypto.RSA.gen_key(1024, 65537)
#proxy_server.save_key ('proxy_server-private.key', None)
#proxy_server.save_pub_key ('proxy_server-public.key')

options.parse_command_line()
logging.info('Proxy server started @ 127.0.0.0:8888')

app = web.Application([(r'.*', ProxyServer),])
http_server = httpserver.HTTPServer(app)
http_server.listen(8888)
ioloop.IOLoop.instance().start()