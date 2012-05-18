import M2Crypto
import os

# M2Crypto.Rand.rand_seed(os.urandom(4096))
proxy_client = M2Crypto.RSA.gen_key(2048, 65537)
proxy_client.save_key ('proxy_client-private.key', None)
proxy_client.save_pub_key ('proxy_client-public.key')
