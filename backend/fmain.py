# The Fastapi web server
from fastapi import FastAPI, status, HTTPException, Body, Request, Depends
from fastapi import responses
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# For API security with API_KEY
from fastapi_simple_security import api_key_router, api_key_security

# JWT support
from jwcrypto.common import JWException

# Import uvicorn for debugging
import uvicorn

import logging

# For the data models
from typing import Dict, Optional, cast
from pydantic import BaseModel, BaseSettings

# The settings for the system
from settings import settings

# For connecting to the blockchain
from blockchain import trustframework as tf
from blockchain import wallet, didutils, safeisland

from eth_account import Account
from eth_keys.datatypes import PrivateKey, PublicKey


# A very fast cache with expiration: https://github.com/tkem/cachetools/
from cachetools import TTLCache


#####################################################
# CONFIGURE THE SERVER
#####################################################

tags_metadata = [
    {
        "name": "Universal Resolver: DID resolution",
        "description": "Operation to resolve a DID.",
    },
    {
        "name": "EBSI-style Verifiable Credentials",
        "description": "Operations related to Verifiable Credentials.",
    },
    {
        "name": "EBSI-style Trusted Issuers registry",
        "description": "Operations related to Trusted Issuers.",
    },
    {
        "name": "Secure Messaging Server",
        "description": "Operations to securely send&receive credentials between participants.",
    },
    {
        "name": "Protected APIs for Issuer",
        "description": "Protected APIs that should not be exposed publicly.",
    },
    {
        "name": "Server Healh Status",
        "description": "To check if the server is working.",
    },
]

app = FastAPI(
    title="EBSI-Alastria Identity APIs",
    description="SSI and Verifiable Credentials with interoperability EBSI-Alastria Red T",
    version="0.9.0",
    openapi_url="/api/v1/openapi.json",
    openapi_tags=tags_metadata
)



# For serving static assets. For the moment just for the test client webapp
app.mount("/static", StaticFiles(directory="statictest"), name="static")

# Template directory. Normally not used, as this is essentially an API server
templates = Jinja2Templates(directory="templates")

# Create the cache for messaging credentials
c = TTLCache(settings.TTLCACHE_NUM_ELEMENTS, settings.TTLCACHE_EXPIRATION)

# Create another cache for 100 DID Documents for 3 hours
doc_cache = TTLCache(100, 3*60*60)

# Create logger
logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)


@app.on_event("startup")
async def startup_event():
    """Connect to blockchain when starting the server"""

    tf.connect_blockchain(settings.BLOCKCHAIN_NODE_IP)
    if settings.PRODUCTION:
        log.warning(f"--- Running in PRODUCTION using bockchain IP: {settings.BLOCKCHAIN_NODE_IP}")
    else:
        log.warning(f"--- Running in DEVELOPMENT using bockchain IP: {settings.BLOCKCHAIN_NODE_IP}")


################################################################################
# PUBLIC APIS (DO NOT NEED AUTHENTICATION)
# Intended for public consumption because they are a "public good"
# They have to be protected from DoS attacks, for example rate-limiting them
# behind a reverse proxy like Nginx
################################################################################

######################################################
# UNIVERSAL RESOLVER: DID RESOLUTION
######################################################

# The reply message
class DIDDocument_reply(BaseModel):
    payload: Dict
    class Config:
        schema_extra = {
            "example": {
                "@context": [
                    "https://www.w3.org/ns/did/v1",
                    "https://w3id.org/security/v1"
                ],
                "id": "did:elsi:VATES-B60645900",
                "publicKey": [
                    {
                        "id": "did:elsi:VATES-B60645900#key-verification",
                        "type": "JwsVerificationKey2020",
                        "controller": "did:elsi:VATES-B60645900",
                        "publicKeyJwk": {
                            "kid": "key-verification",
                            "kty": "EC",
                            "crv": "secp256k1",
                            "x": "QoHDiX_hLAm7M__qUyCXRod6jzx0tCxS-_RoIjP1xzg",
                            "y": "Tqp4fFlMb6YcW-3b86kKjcpx8TyIg4Mkb5Q3nB5bgq4"
                        }
                    }
                ],
                "service": [
                    {
                        "id": "did:elsi:VATES-B60645900#info",
                        "type": "EntityCommercialInfo",
                        "serviceEndpoint": "www.in2.es",
                        "name": "IN2"
                    }
                ],
                "alaExtension": {
                    "redT": {
                        "domain": "in2.ala",
                        "ethereumAddress": "0x202e88FA672F65810e5Ed0EF84fFe919063d4E60"
                    }
                },
                "created": "2020-12-23T13:35:23Z",
                "updated": "2020-12-23T13:35:23Z"
            }
        }

# Resolves a DID and returns the DID Document (JSON format), if it exists
# We support four DID methods: ebsi, elsi, ala, peer.
# TODO: talk to LACChain to support DIDs coming from them
@app.get("/api/did/v1/identifiers/{DID}", response_model=DIDDocument_reply, tags=["Universal Resolver: DID resolution"])
def resolve_DID(DID: str):
    """Resolves a DID and returns the DID Document (JSON format), if it exists.  
    We support four DID methods: **ebsi**, **elsi**, **ala**, **peer**.

    Only **PEER** and **ELSI** (*https://github.com/hesusruiz/SafeIsland#62-elsi-a-novel-did-method-for-legal-entities*) are directly
    implemented by this API.
    The others are delegated to be resolved by their respective implementations.

    For example, for **EBSI** we call the corresponding Universal Resolver API, currently in testing and available at
    *https://api.ebsi.xyz/did/v1/identifiers/{did}*
    """

    # Parse the DID and check if it is one of the supported types
    try:
        err, did_struct = didutils.parseDid(DID)
    except Exception as e:
        detail=str(e)
        log.error(detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    if err:
        log.error(err)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    # DIDs and associated DID Documents do not change a lot after creation
    # Caching the DID Documents for several hours is an acceptable compromise
    # and can increase performance substantially (default: 3 hours)
    # Check if the DID is already in the cache
    didDoc = cast(dict, doc_cache.get(DID))
    if didDoc is not None:
        return {"payload": didDoc}   

    did_method = did_struct["method"]

    # Process ELSI DID method
    if did_method == "elsi":

        # Try to resolve from the blockchain node
        try:
            _DID, name, didDoc, active = tf.resolver.resolveDID(DID)
        except Exception as e:
            detail=str(e)
            log.error(detail)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
  
        if didDoc is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DID not found")

        # Store the DID and associated DIDDocument in the cache
        doc_cache[DID] = didDoc

        return {"payload": didDoc}

    # Process EBSI DID method
    elif did_method == "ebsi":

        # When EBSI reaches production, we will resolve the DID using the API
        # which now is at: 
        # Note that it is a Universal Resolver API like this one
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not implemented")

    # Process AlastriaID DID method
    elif did_method == "ala":

        # When AlastriaID (standard) reaches production, we will resolve the DID
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not implemented")

    # Process Peer DID method
    elif did_method == "peer":

        # TODO: implement the Peer DID
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not implemented")

    # Should not reach here
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="DID parsing failed")

    
######################################################
# Lists the Trusted Issuers in the system
######################################################

@app.get("/api/trusted-issuers-registry/v1/issuers", tags=["EBSI-style Trusted Issuers registry"])
def list_trusted_issuers():
    """Returns the list of all trusted issuers registered in the blockchain for the SafeIsland ecosystem.
    """

    # Query the blockchain and manage exceptions
    try:
        trusted_issuers = tf.dump_trusted_identities()
    except Exception as e:
        detail=str(e)
        log.error(detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    return {"payload": trusted_issuers}


#####################################################
# Verify a Credential, checking its digital signature
# with the Identity of the Issuer in the Blockchain
#####################################################

# The message that is sent or received, with an opaque payload (but must be string)
class VerifyJWTMessage(BaseModel):
    payload: str    # The JWT in JWS Compact Serialization format as specified in IETF RFC 7519
    class Config:
        schema_extra = {
            "example": {
                "payload": "The JWT in JWS Compact Serialization format as specified in IETF RFC 7519"
            }
        }


@app.post("/api/verifiable-credential/v1/verifiable-credential-validations", tags=["EBSI-style Verifiable Credentials"])
def credential_verify(msg: VerifyJWTMessage):
    """Verify a Credential in JWT format, checking its digital signature
    with the Identity of the Issuer in the Blockchain.
    """

    # Check if we have received some data in the POST
    jwt_cert = msg.payload
    if len(jwt_cert) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data received")

    # Verify the certificate
    print(len(jwt_cert))
    print(jwt_cert)
    try:
        claims = safeisland.verify_cert_token(jwt_cert)
    except JWException as e:
        detail=str(e)
        log.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
    except Exception as e:
        detail=str(e)
        log.error(detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    
    if claims is None:
        log.error("Verification of token failed")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification of token failed")

    # If we reached here, the JWT was verified and can return the claims in JSON format
    return {"payload": claims}


#####################################################
# MESSAGING SERVER
#####################################################

# The message that is sent or received, with an opaque payload (but must be string)
class Message(BaseModel):
    payload: str


@app.post("/api/write/{sessionKey}", tags=["Secure Messaging Server"])
def write_item(sessionKey: str, msg: Message):
    """Write a payload to the cache associated to a sessionKey.
    This API is used to send a Credential to a receiver. It is used by:
    1. The Issuer when sending a credential to the Passenger
    2. The Passenger when sending a credential to the Verifier
    """

    # Check if we have received some data in the POST
    if len(msg.payload) == 0:
        log.error("No data received")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data received")

    # Store in the cache and return the session key
    c[sessionKey] = msg.payload
    return {"sessionKey": sessionKey}


@app.get("/api/read/{sessionKey}", response_model=Message, tags=["Secure Messaging Server"])
def read_item(sessionKey):
    """Read the payload from the cache specifying the unique sessionKey.
    This API is used to receive a Credential from a sender. It is used by:
    1. The Issuer when receiving a credential from the Issuer
    2. The Verifier when receiving a credential from the Passenger
    """

    # Try to get the element from the cache, erasing it if it exists
    payload = c.pop(sessionKey, "")
    return {"payload": payload}



################################################################################
# PROTECTED APIS (REQUIRE AUTHENTICATION)
# Intended for Issuer
# Intended for Issuer
# Intended for Issuer
# Intended for Issuer
################################################################################

#####################################################
# APIS FOR USAGE BY THE ISSUER MOBILE APP
#####################################################

# Get a list of credentials from the database in the server in JSON
#@app.get("/api/verifiable-credential/v1/credentials", tags=["Protected APIs for Issuer"], dependencies=[Depends(api_key_security)])
@app.get("/api/verifiable-credential/v1/credentials", tags=["Protected APIs for Issuer"])
def credential_list():
    """Get a list of credentials from the database in the server in JSON
    """
    rows = safeisland.list_certificates()
    certs = []
    for row in rows:
#        certs.append(row["cert"])
        certs.append({"uuid": row["uuid"], "cert": row["cert"]})

    return {"payload": certs}


# Gets a credential (JSON) from issuer by specifying its uniqueID
@app.get("/api/verifiable-credential/v1/{uniqueID}", tags=["Protected APIs for Issuer"])
def credential_get(uniqueID: str):
    """Gets a credential (JSON) from issuer by specifying its uniqueID
    """

    cert = safeisland.certificate(uniqueID)
    return {"payload": cert}


#####################################################
# CREATE A PRIVATE KEY
#####################################################

# The reply message
class CreatePrivateKey_reply(BaseModel):
    kty: str
    crv: str
    d: str
    x: str
    y:str


@app.post("/api/wallet/v1/privatekey", response_model=CreatePrivateKey_reply, tags=["Protected APIs for Issuer"])
def create_privatekey():
    """ Create a private key that can be used to create an identity in the blockchain
    """
    
    # Generate the private key
    key_jwk = wallet.create_JWK()
    response_jwk = key_jwk.export(private_key=True, as_dict=True)

    return response_jwk

@app.get("/api/wallet/v1/privatekey/{account}/{password}", response_model=CreatePrivateKey_reply, tags=["Protected APIs for Issuer"])
def get_privatekey(account: str, password: str):
    """Get an existing private key in the wallet.
    Must specify an existing account name and its password
    """
    
    key_jwk = wallet.key_JWK(account, password)
    response_jwk = key_jwk.export(private_key=True, as_dict=True)

    return response_jwk


#######################################################
# CREATE AN IDENTITY AS A SUBNODE FROM THE CALLER NODE
#######################################################

# The input message

class PublickeyJWK(BaseModel):
    kty: str
    crv: str
    x: str
    y:str

class PrivatekeyJWK(PublickeyJWK):
    d: str

class CreateIdentity_request(BaseModel):
    DID: str                            # ELSI DID of the new identity, example: "did:elsi:VATES-B60645900"
    domain_name: str                    # Blockchain domain name to assign, example: "in2.ala"
    website: str                        # Website of the entity, example: "www.in2.es"
    commercial_name: str                # Commercial name, example: "IN2 Innovating 2gether"
    new_privatekey: PrivatekeyJWK         # The private key of the new entity
    parent_privatekey: PrivatekeyJWK    # The Private Key of caller (in this case the owner of "ala")

    class Config:
        schema_extra = {
            "example": {
                "DID": "did:elsi:VATES-B60645900",
                "domain_name": "in2.ala",
                "website": "www.in2.es",
                "commercial_name": "IN2 Innovating 2gether",
                "new_privatekey": {
                    "kty": "EC",
                    "crv": "secp256k1",
                    "d": "Dqv3jmu8VNMKXWrHkppr5473sLMzWBczRhzdSdpxDfI",
                    "x": "FTiW0a4r7S2SwjL7AlFlN1yJNWF--4_x3XTTxkFbJ9o",
                    "y": "MmpxbQCOZ0L9U6rLLkD_U8LRGwYEHcoN-DPnEdlpt6A"
                },
                "parent_privatekey": {
                    "kty": "EC",
                    "crv": "secp256k1",
                    "d": "Dqv3jmu8VNMKXWrHkppr5473sLMzWBczRhzdSdpxDfI",
                    "x": "NKW_0Fs4iumEegzKoOH0Trwtje1sXsG9Z1949sA8Omo",
                    "y": "g4B3EI0qIdlcXTn-2RpUxgVX-sxNFdqCQDD0aHztVkk"
                }
            }
        }


# The reply message
class CreateIdentity_reply(BaseModel):
    didDoc: Dict


@app.post("/api/did/v1/identifiers", response_model=CreateIdentity_reply, tags=["Protected APIs for Issuer"])
def create_identity(msg: CreateIdentity_request):
    """Create an Identity anchored in the blockchain
    """
    
    # Check if we have received some data in the POST
    if len(msg.DID) == 0:
        log.error("No data received")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data received")

    # Create the identity using the library
    try:
        error, didDoc = tf.create_identity_subnode(
            msg.DID, msg.domain_name, msg.website, msg.commercial_name, msg.new_privatekey, msg.parent_privatekey)
    except Exception as e:
        detail=str(e)
        log.error(detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    if error is not None:
        log.error(error)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return {"didDoc": didDoc.to_dict()}

# The input message, assuming the server has a wallet
class CreateIdentity_request_wallet(BaseModel):
    DID: str                    # ELSI DID of the new identity, example: "did:elsi:VATES-B60645900"
    domain_name: str            # Blockchain domain name to assign, example: "in2.ala"
    website: str                # Website of the entity, example: "www.in2.es"
    commercial_name: str        # Commercial name, example: "IN2 Innovating 2gether"
    parent_node_account: str    # Account that owns the parent node, example: "Alastria"
    password: str               # Password to encrypt private key, example: "ThePassword"

    class Config:
        schema_extra = {
            "example": {
                "DID": "did:elsi:VATES-B60645900",
                "domain_name": "in2.ala",
                "website": "www.in2.es",
                "commercial_name": "IN2 Innovating 2gether",
                "parent_node_account": "Alastria",
                "password": "ThePassword"
            }
        }



@app.post("/api/did/v1/wallet/identifiers", response_model=CreateIdentity_reply, tags=["Protected APIs for Issuer"])
def create_identity_with_wallet(msg: CreateIdentity_request_wallet):
    """Create an identity anchored in the blockchain, using an existing account in the server
    """
    
    # Check if we have received some data in the POST
    if len(msg.DID) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data received")

    # Create the identity using the library
    error, didDoc = tf.create_identity(
        msg.DID, msg.domain_name, msg.website, msg.commercial_name, msg.parent_node_account, msg.password)
    if error is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return didDoc.to_dict()


#####################################################
# HEALTH CHECKING
#####################################################
@app.get("/api/ping", tags=["Server Healh Status"])
def ping(request: Request):
    """A simple ping to check for server health
    """
    client_host = request.client.host
    return {"payload": "Hello, v1.0.1", "client": client_host}


app.include_router(api_key_router, prefix="/auth", tags=["API-key Authorization"])



if __name__ == "__main__":
    uvicorn.run("fmain:app", host="127.0.0.1", port=8000, reload=True)