import M2Crypto
import os

M2Crypto.Rand.rand_seed(os.urandom(2048))
proxy_client = M2Crypto.RSA.gen_key(2048, 65537)
proxy_client.save_key ('proxy_client-private.key', None)
proxy_client.save_pub_key ('proxy_client-public.key')
