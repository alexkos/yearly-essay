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

class ProxyServer(web.RequestHandler):

    def gen_key_aes(self):
        blocksize = 32
        secret_key = os.urandom(blocksize)
        return secret_key

    def encrypt_body(self, secret_key, enc_body):
        cipher = AES.new(secret_key)
        padding = '{'
        blocksize = 32        
        pad = lambda s: s + (blocksize - len(s) % blocksize) * padding
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
        
        encoded_body = EncodeAES(cipher, enc_body)

        return encoded_body

    def encrypt_key_aes(self, key_secret_aes):
        public_key = M2Crypto.RSA.load_pub_key('proxy_client-public.key')
        print('#========================================================================#')
        print(len(public_key))
        print('#========================================================================#')
        encrypt_key = public_key.public_encrypt(key_secret_aes, M2Crypto.RSA.pkcs1_oaep_padding)
        print('#--------------------------------------------------------------------#')
        print(len(key_secret_aes))
        print('#--------------------------------------------------------------------#')
        key_encode_base64 = base64.b64encode(encrypt_key)

        return key_encode_base64

    def response_client(self, response):
        key_aes = self.gen_key_aes()

        if options.encrypt == 'yes':
            self.add_header('x-Encrypt', self.encrypt_key_aes(key_aes))
            self.write(self.encrypt_body(key_aes, response.body))
        else:
            self.write(response.body)
        
        self.flush()
        self.finish()

    @web.asynchronous
    def get(self):
        request_client = HTTPRequest(url = self.request.uri, method = self.request.method, body = self.request.body or None, \
            headers = self.request.headers)
        http_client = CurlAsyncHTTPClient()
        response = http_client.fetch(request_client, self.response_client)

tornado.options.parse_command_line()
if options.encrypt:
    logging.info('Proxy server started @%s:%s Encrypt:%s' % (options.host, options.port, options.encrypt)) 
else:
    logging.info('Proxy server started @%s:%s' % (options.host, options.port)) 

app = web.Application([(r'.*', ProxyServer),])
http_server = httpserver.HTTPServer(app)
http_server.listen(options.port)
ioloop.IOLoop.instance().start()