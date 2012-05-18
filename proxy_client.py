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

define("ip_address", default= 'localhost', help="run on the given port", type=str)
define("port", default=8080, help="run on the given port", type=int)
define("ip_address_proxy", default= 'localhost', help="run on the given port", type=str)
define("port_proxy", default=8888, help="run on the given port", type=int)

class ProxyClient(web.RequestHandler):

    #decoding body with help key AES
    def decrypt_body(self, key_aes):
        cipher = AES.new(key_aes)
        padding = '{'
        DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(padding)
        decoded_body = DecodeAES(cipher, response.body)

        return decoded_body

    def decrypt_key_aes(self, encrypt_key):
        #decrypt key AES
        decode_key = base64.b64decode(encrypt_key)
        secret_key = M2Crypto.RSA.load_key ('proxy_client-private.key')
        key_aes = secret_key.private_decrypt (decode_key, M2Crypto.RSA.pkcs1_oaep_padding)

        return key_aes

    def response_client(self, response):
        if 'x-Encrypt' in response.headers:
            self.write(self.decrypt_body(decrypt_key_aes(response.headers['x-Encrypt'])))
        else:
            self.write(response.body)
        self.finish()

    @web.asynchronous
    def get(self):
        request_client = HTTPRequest(url = self.request.uri, method = self.request.method, body = self.request.body or None, \
            headers = self.request.headers, proxy_host = options.ip_address_proxy, proxy_port = options.port_proxy)
        http_client = CurlAsyncHTTPClient()
        response = http_client.fetch(request_client, self.response_client)

tornado.options.parse_command_line()
logging.info('Client server started @%s:%s -> proxy server: %s:%s' % (options.ip_address, options.port, options.ip_address_proxy, options.port_proxy))

app = web.Application([(r'.*', ProxyClient),])
http_server = httpserver.HTTPServer(app)
http_server.listen(options.port)
ioloop.IOLoop.instance().start()