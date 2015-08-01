from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util import randpool
import base64
import urllib2
"""
generate key:
key = randpool.RandomPool(512).get_bytes(16) #byte array
readablekey = base64.b64encode(key)
usablekey = base64.b64decode(usablekey)
"""

"""
USAGE:

c = Cipher()
enc = c.encrypt('Boing boing boing')
print enc # SxXJUcXkQ6uq05VwtT6xnN4=
c = Cipher()
plain = c.decrypt(enc)
print plain # Boing boing boing
"""

class Cipher:
	def __init__(self, key='qu3RRLUWwC2YicenGfmz31zkT+pOYRPlts7A1JeuOVU=', iv='5sYi6x5ZNpwYzSQ5D8obDw=='):
		key = base64.b64decode(key)
		iv = base64.b64decode(iv)
		self.cipher = AES.new(key, AES.MODE_CFB, iv)

	def encrypt(self, string):
		enc = self.cipher.encrypt(string)
		return urllib2.quote(base64.urlsafe_b64encode(enc))

	def decrypt(self, string):
		enc = base64.urlsafe_b64decode(urllib2.unquote(string))
		return str(self.cipher.decrypt(enc))


