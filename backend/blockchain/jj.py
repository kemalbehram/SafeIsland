import os
import sqlite3
import json
from sqlite3.dbapi2 import Connection
from eth_utils.crypto import keccak
from hexbytes import HexBytes
from dataclasses import dataclass

from jwcrypto import jwt, jwk, jws

from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_keys.datatypes import PrivateKey, PublicKey
from jwcrypto.common import base64url_decode, base64url_encode


from pprint import pprint as pp


# Create an Ethereum account
eth_acc = Account.create()
eth_pubKey = PublicKey.from_private(eth_acc._key_obj).to_hex()
eth_privKey = eth_acc.privateKey.hex()


# Create a JWK key
jwk_key = jwk.JWK.generate(kty='EC', crv="secp256k1")
jwk_key_export = jwk_key.export(as_dict=True)



Token = jwt.JWT(
    algs=["ES256K"],
    header={"alg": "ES256K"},
    claims={"info": "I'm a signed token"},
    default_claims={"iat": None, "exp": None}
    )


Token.make_signed_token(jwk_key)
st = Token.serialize()

print(f"Serialized token: {st}")

OT = jwt.JWT(jwt=st, algs=["ES256K"])
print(f"Token claims: {OT.token}")
