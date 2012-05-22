import os
import base64
import logging
import M2Crypto
import tornado.options
from tornado import web
from tornado import ioloop 
from Crypto.Cipher import AES
from tornado import httpserver
from tornado.httpclient import HTTPRequest
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.options import define, options

define("host", default= 'localhost', help="run on the given port", type=str)
define("port", default=8080, help="run on the given port", type=int)
define("host_proxy", default= 'localhost', help="run on the given port", type=str)
define("port_proxy", default=8888, help="run on the given port", type=int)
define("client_private_key", default='proxy_client-private.key', help="", type=str)
define("server_public_key", default='proxy_server-private.key', help="", type=str)

class ProxyClient(web.RequestHandler):

    def decrypt_body(self, key_aes, response):
        cipher = AES.new(key_aes)
        padding = '{'
        DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(padding)
        decoded_body = DecodeAES(cipher, response.body)

        return decoded_body

    def decrypt_key_aes(self, encrypt_key):
        decode_key = base64.b64decode(encrypt_key)
        secretkey = M2Crypto.RSA.load_key(options.client_private_key)
        key = secretkey.private_decrypt(decode_key,M2Crypto.RSA.pkcs1_oaep_padding)

        return key

    def check_signature(self, decsign, checksign):
        check_sign = False
        sign = base64.b64decode(decsign)
        key = base64.b64decode(checksign)
        secretkey = M2Crypto.RSA.load_key (options.server_public_key)
        chkey = secretkey.private_decrypt(sign, M2Crypto.RSA.pkcs1_oaep_padding)

        if chkey == key:
            check_sign = True

        return check_sign

    def response_client(self, response):        
        if 'x-Encrypt' in response.headers:
            Encrypt = response.headers['x-Encrypt']
            Signature = response.headers['x-Signature']
            
            check = self.check_signature(Signature,Encrypt)
            if check:
                self.write(self.decrypt_body(self.decrypt_key_aes(Encrypt),response))
            else:
                self.write('Content is not correct!')
        else:
            self.write(response.body)
        if self._headers.has_key('Content-Type'):
            del self._headers['Content-Type']
        self.finish()

    @web.asynchronous
    def get(self):
        request_client = HTTPRequest(url = self.request.uri, 
                                    method = self.request.method, 
                                    body = self.request.body or None,
                                    headers = self.request.headers, 
                                    proxy_host = options.host_proxy, 
                                    proxy_port = options.port_proxy)
        http_client = CurlAsyncHTTPClient()
        response = http_client.fetch(request_client, self.response_client)

tornado.options.parse_command_line()
logging.info('Client server started @%s:%s -> proxy server: %s:%s'%\
    (options.host, options.port, options.host_proxy, options.port_proxy))

app = web.Application([(r'.*', ProxyClient),])
http_server = httpserver.HTTPServer(app)
http_server.listen(options.port,options.host)
ioloop.IOLoop.instance().start()
