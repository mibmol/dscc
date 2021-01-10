from datetime import datetime, timedelta
from random import randint
import hashlib
import base64
import json

app_login = '1764408d'
app_secret = '28W'

MIN_NONCE= 10000000
MAX_NONCE= 99999999

def generate_auth():
	now = datetime.now().astimezone().replace(microsecond=0)
	nonce = randint(MIN_NONCE, MAX_NONCE)
	nonce_b64 = base64.b64encode(str(nonce).encode('utf-8'))
	seed = (now + timedelta(minutes=7)).isoformat()

	hash_digest = hashlib.sha1(f"{nonce}{seed}{app_secret}".encode("utf-8")).digest()
	tran_key = base64.b64encode(hash_digest)
	auth_obj = {
		"login": app_login,
		"tranKey": tran_key.decode("utf-8"),
		"nonce": nonce_b64.decode("utf-8"),
		"seed": seed
	}
	print(json.dumps(auth_obj))
	return auth_obj


def decode():
	tranKey = "NzZjNDRiZTcwMjMyOWFiYzkyYWZkNGUwYjE4YjcxNTk5MTA4NmY5ZmQxYjU2ZDZmZGU3ZGYxMmVhNDE5MmEzZQ=="
	digest = base64.b64decode(tranKey.encode('utf-8')).decode('utf-8')
	print("digest: ", digest)

generate_auth()
#decode()