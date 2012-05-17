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

    def gen_key_aes(self):
        blocksize = 32
        secret_key = os.urandom(blocksize)
        cipher = AES.new(secret)
        return cipher

    def encrypt_body(self, cipher, enc_body):
        padding = '{'
        pad = lambda s: s + (blocksize - len(s) % blocksize) * padding
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
        encoded_body = EncodeAES(cipher, enc_body)
        return encoded_body

    def response_client(self, response):
        print('#-------------------------------------------------------#')
        print(response.headers)
        print('#-------------------------------------------------------#')
        key_aes = self.gen_key_aes()
        public_key = M2Crypto.RSA.load_pub_key('proxy_client-public.key')
        encrypt_key = public_key.public_encrypt(key_aes, M2Crypto.RSA.pkcs1_oaep_padding)

        key_encode_base64 = base64.b64encode(encrypt_key)

        self.write(self.encrypt_body(key_aes, response.body))
        self.add_header('x-Encrypt', key_encode_base64)
        self.finish()

    @web.asynchronous
    def get(self):
        request_client = HTTPRequest(url = self.request.uri, method = self.request.method, body = self.request.body or None, \
            headers = self.request.headers)
        http_client = CurlAsyncHTTPClient()
        response = http_client.fetch(request_client, self.response_client)

options.parse_command_line()
logging.info('Proxy server started @ 127.0.0.0:8888')

app = web.Application([(r'.*', ProxyServer),])
http_server = httpserver.HTTPServer(app)
http_server.listen(8888)
ioloop.IOLoop.instance().start()