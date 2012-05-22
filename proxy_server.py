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
define("port", default=8888, help="run on the given port", type=int)
define("encrypt", default='yes', help="run on the encrypt body", type=str)
define("blocksize", default=32, help="run on the encrypt body", type=int)
define("client_public_key", default='proxy_client-public.key', help="", type=str)
define("server_private_key", default='proxy_server-public.key', help="", type=str)


class ProxyServer(web.RequestHandler):

    def gen_key_aes(self):
        secret_key = os.urandom(options.blocksize)
        return secret_key

    def encrypt_body(self, secret_key, enc_body):
        cipher = AES.new(secret_key)
        padding = '{'
        pad = lambda s: s+(options.blocksize-len(s)%options.blocksize)*padding
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
        
        encoded_body = EncodeAES(cipher, enc_body)

        return encoded_body

    def encrypt_key_aes(self, key_aes):
        publickey = M2Crypto.RSA.load_pub_key(options.client_public_key)
        encryptkey = publickey.public_encrypt(key_aes, M2Crypto.RSA.pkcs1_oaep_padding)

        return encryptkey

    def digital_signature(self, key):
        secretkey = M2Crypto.RSA.load_pub_key(options.server_private_key)
        sign = secretkey.public_encrypt(key, M2Crypto.RSA.pkcs1_oaep_padding)

        return sign

    def response_client(self, response):
        key_aes = self.gen_key_aes()
        encrypt_key = self.encrypt_key_aes(key_aes)
        signature = self.digital_signature(encrypt_key)

        key_encode_base64 = base64.b64encode(encrypt_key)
        sign_encode_base64 = base64.b64encode(signature)

        if response.headers.has_key('Content-Type'):
            del response.headers['Content-Type']

        if options.encrypt == 'yes':
            self.add_header('x-Encrypt', key_encode_base64)
            self.add_header('x-Signature', sign_encode_base64)
            self.write(self.encrypt_body(key_aes, response.body))
        else:
            self.write(response.body)
        
        self.flush()
        self.finish()

    @web.asynchronous
    def get(self):
        request_client = HTTPRequest(url = self.request.uri, 
                                     method = self.request.method,
                                     body = self.request.body or None,
                                     headers = self.request.headers)
        http_client = CurlAsyncHTTPClient()
        response = http_client.fetch(request_client, self.response_client)

tornado.options.parse_command_line()
if options.encrypt:
    logging.info('Proxy server started @%s:%s Encrypt:%s' % \
        (options.host, options.port, options.encrypt)) 
else:
    logging.info('Proxy server started @%s:%s' % (options.host, options.port)) 

app = web.Application([(r'.*', ProxyServer),])
http_server = httpserver.HTTPServer(app)
http_server.listen(options.port)
ioloop.IOLoop.instance().start()