# The Fastapi web server
from fastapi import FastAPI, status, HTTPException, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# JWT support
from jwcrypto.common import JWException

# Import uvicorn for debugging
import uvicorn

# For the data models
from typing import Dict, Optional, cast
from pydantic import BaseModel, BaseSettings

# For connecting to the blockchain
from blockchain import trustframework as tf
from blockchain import wallet, certificates, didutils

# SQLite for storing persistent data
import sqlite3

# A very fast cache with expiration: https://github.com/tkem/cachetools/
from cachetools import TTLCache


#####################################################
# CONFIGURE THE SERVER
#####################################################

class Settings(BaseSettings):
    MAX_CONTENT_LENGTH: int = 30000
    TTLCACHE_NUM_ELEMENTS: int = 10000
    TTLCACHE_EXPIRATION: int = 60
    BLOCKCHAIN_NODE_IP: str = tf.BLOCKCHAIN_NODE_IP_PRODUCTION

settings = Settings()
app = FastAPI(
    title="EBSI-Alastria Identity APIs",
    description="SSI and Verifiable Credentials with interoperability EBSI-Alastria Red T",
    version="0.9.0",
    openapi_url="/api/v1/openapi.json"
)

tags_metadata = [
    {
        "name": "Universal Resolver: DID resolution",
        "description": "Operation to resolve a DID.",
    },
    {
        "name": "Wallet and Identities",
        "description": "Operations to create and manage identities.",
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
        "name": "Server Health Status",
        "description": "To check if the server is working.",
    },
]


# For serving static assets. For the moment just for the test client webapp
app.mount("/static", StaticFiles(directory="statictest"), name="static")

# Template directory. Normally not used, as this is essentially an API server
templates = Jinja2Templates(directory="templates")

# Create the cache for messaging credentials
c = TTLCache(settings.TTLCACHE_NUM_ELEMENTS, settings.TTLCACHE_EXPIRATION)

# Create another cache for 100 DID Documents for 3 hours
doc_cache = TTLCache(100, 3*60*60)

# Connect to blockchain when starting the server
tf.connect_blockchain()


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
    err, did_struct = didutils.parseDid(DID)
    if err:
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
        _DID, name, didDoc, active = tf.resolver.resolveDID(DID)
        if didDoc is None:
            return {"payload": ""}

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

    # Query the blockchain an dmanage exceptions
    try:
        trusted_issuers = tf.dump_trusted_identities()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.args)

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
    try:
        claims = certificates.verify_cert_token(jwt_cert)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.args)
    
    if claims is None:
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
@app.get("/api/verifiable-credential/v1/credentials", tags=["Protected APIs for Issuer"])
def credential_list():
    rows = certificates.list_certificates()
    certs = []
    for row in rows:
        certs.append(row["diag_id"])

    return {"payload": certs}


# Gets a credential (JSON) from issuer by specifying its uniqueID
@app.get("/api/verifiable-credential/v1/{uniqueID}", tags=["Protected APIs for Issuer"])
def credential_get(uniqueID: str):
    cert = certificates.certificate(uniqueID)
    return {"payload": cert}


#####################################################
# CREATE AN IDENTITY
#####################################################

# The input message
class CreateIdentity_request(BaseModel):
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


# The reply message
class CreateIdentity_reply(BaseModel):
    didDoc: Dict


@app.post("/api/did/v1/identifiers", tags=["Protected APIs for Issuer"])
def create_identity(msg: CreateIdentity_request):
    
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
@app.get("/api/ping", tags=["Healh status"])
def ping():
    return {"payload": "Hello, v1.0.1"}





if __name__ == "__main__":
    uvicorn.run("fmain:app", host="127.0.0.1", port=8000, reload=True)