#!/usr/bin/python3
from typing import Any, Dict, Tuple
import xml.etree.ElementTree as ET
import urllib
import click
import os
import inspect
import ast
import subprocess as sp
import requests
import logging
from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_keys.datatypes import PrivateKey, PublicKey
import json
import sqlite3
from pprint import pprint
from hexbytes import HexBytes
from typing_extensions import Annotated
from jwcrypto.common import base64url_decode, base64url_encode


from blockchain import redt as b
from blockchain import wallet

from ens.utils import label_to_hash, raw_name_to_hash

###########################################
# Set this flag to set the environment
###########################################
PRODUCTION = True
###########################################
###########################################


# The directory where the tool is invoked
INITIAL_DIR = os.getcwd()

# Directories with sources of the Smart Contracts and deployment artifacts
CONTRACTS_DIR = os.path.join(INITIAL_DIR, "smartcontracts", "src")
CONTRACTS_OUTPUT_DIR = os.path.join(
    INITIAL_DIR, "smartcontracts", "test_deploy")
if PRODUCTION:
    CONTRACTS_OUTPUT_DIR = os.path.join(
        INITIAL_DIR, "smartcontracts", "deploy")

# Location of Solidity compiler
SOLC_DIR = os.path.join(INITIAL_DIR, "solc")

# Location of EUTL input files (XML format)
TRUSTED_LISTS_DIR = os.path.join(INITIAL_DIR, "eutl")

# Location and name of the SQLite database with local config data
DATABASE_DIR = os.path.join(INITIAL_DIR)
DATABASE_NAME = os.path.join(DATABASE_DIR, "pubcred_config.sqlite")

# Address of the blockchain node to use (development/production)
BLOCKCHAIN_NODE_IP_PRODUCTION = "HTTP://15.236.0.91:22000"
BLOCKCHAIN_NODE_IP_DEVELOPMENT = "HTTP://127.0.0.1:7545"
BLOCKCHAIN_NODE_IP = BLOCKCHAIN_NODE_IP_DEVELOPMENT

if PRODUCTION:
    BLOCKCHAIN_NODE_IP = BLOCKCHAIN_NODE_IP_PRODUCTION


# Initialize some global variables
ENS = None
PublicResolver = None
ens = None
resolver = None

# Initialize logging
log = logging.getLogger(__name__)


####################################################
####################################################
# START: DIDDocument management

# The class representing a DIDDocument for a public entity (legal person)
class DIDDocument:

    def __init__(self, DID: str = None, node_name: str = None, label: str = None, address: str = None, publicKey: bytes = None, manager_account=None):

        self.label = label
        self.node_name = node_name
        self.domain_name = label + "." + node_name
        self.address = address
        self.publicKey = publicKey
        self.manager_account = manager_account

        self.alaExtension = {
            "redT": {
                "domain": self.domain_name,
                "ethereumAddress": self.address
            }
        }

        self.doc = {
            "@context": ["https://www.w3.org/ns/did/v1", "https://w3id.org/security/v1"],
            "id": DID,
            "publicKey": [],
            "service": [],
            "alaExtension": self.alaExtension,
            "created": "",
            "updated": ""
        }
        self.addPublicKey("key-verification",
                          "JwsVerificationKey2020", publicKey)
        self.setCreated()

    def __str__(self):
        return json.dumps(self.doc, ensure_ascii=False, indent=3)

    @classmethod
    def from_object(self, didDoc: Any):
        self.doc = didDoc
    
    def to_dict(self):
        return self.doc

    def setDID(self, DID):
        self.doc["id"] = DID
        self.setUpdated()

    def DID(self):
        return self.doc["id"]

    def addService(self, service: dict):

        self.doc["service"].append(service)
        self.setUpdated()

    def addPublicKey(self, kid: str, key_type: str, publicKey: bytes):

        # TODO: Use the public key thumbprint for kis (RFC 7638)

        # The public key is 64 bytes composed of the x and y curve coordinates
        # x and y are each 32 bytes long
        # We convert x and y to hex, so the dictionary can be converted to JSON
        x = publicKey[:32]
        y = publicKey[32:]

        # Create the Json Web Key (JWK) representation, as specified by W3C DID Document format
        publicKey_JWK = {
            "id": self.doc["id"]+"#"+kid,
            "type": key_type,
            "controller": self.doc["id"],
            "publicKeyJwk": {
                "kid": kid,
                "kty": "EC",
                "crv": "secp256k1",
                #                "x": x.hex(),
                #                "y": y.hex()
                "x": base64url_encode(x),
                "y": base64url_encode(y)
            }
        }

        self.doc["publicKey"].append(publicKey_JWK)
        self.setUpdated()

    def addRefPublicKey(self, reference):
        did = self.doc["id"]
        self.doc["publicKey"].append(did+reference)
        self.setUpdated()

    def setCreated(self):
        import datetime as dat
        now = dat.datetime.now(dat.timezone.utc)
        formatted_now = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.doc["created"] = formatted_now
        self.doc["updated"] = formatted_now

    def setUpdated(self):
        import datetime as dat
        now = dat.datetime.now(dat.timezone.utc)
        formatted_now = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.doc["updated"] = formatted_now

    # Create the Identity associated to the DIDDocument
    def createIdentity(self, ens, resolver):

        # Set the DID and DIDDocument
        print(json.dumps(self.doc, ensure_ascii=False, indent=3))
        success, tx_receipt, tx_hash = resolver.setAlaDIDPublicEntity(
            node_name=self.node_name,
            label=self.label,
            DID=self.DID(),
            name=self.domain_name,
            DIDDocument=json.dumps(self.doc, ensure_ascii=False, indent=3),
            active=True,
            new_owner_address=self.address,
            caller_key=self.manager_account.key
        )
        return success, tx_receipt, tx_hash

# END: DIDDocument management
####################################################
####################################################


####################################################
####################################################
# START: ENS
class ENS_class:

    def __init__(self):

        self.initialized = True

    def setRootAccount(self, root_account):
        self.root_account = root_account

    def resolver(self, node_name="root"):

        if node_name == "root":
            node_hash = b.to_32byte_hex(0)
        else:
            node_hash = raw_name_to_hash(node_name)

        node_hash = raw_name_to_hash(node_name)

        Resolver_address = ENS.functions.resolver(node_hash).call()
        return Resolver_address

    def owner(self, node_name="root"):
        node_hash = raw_name_to_hash(node_name)
        owner = ENS.functions.owner(node_hash).call()
        return owner

    def setSubnodeOwner(self, node_name="root", label=None, new_owner_address=None, current_owner_key=None):

        if node_name == "root":
            node_hash = b.to_32byte_hex(0)
        else:
            node_hash = raw_name_to_hash(node_name)

        label_hash = label_to_hash(label)

        contract_fun = ENS.functions.setSubnodeOwner(
            node_hash,
            label_hash,
            new_owner_address)
        success, tx_receipt, tx_hash = b.send_signed_tx(
            contract_fun, current_owner_key)
        return success, tx_receipt, tx_hash

    def setApprovalForAll(self, operator_address, approved, current_owner_key):

        contract_fun = ENS.functions.setApprovalForAll(
            operator_address,
            approved)
        success, tx_receipt, tx_hash = b.send_signed_tx(
            contract_fun, current_owner_key)
        return success, tx_receipt, tx_hash

    def setResolver(self, node_name="root", resolver_address=None, current_owner_key=None):

        if node_name == "root":
            node_hash = b.to_32byte_hex(0)
        else:
            node_hash = raw_name_to_hash(node_name)

        contract_fun = ENS.functions.setResolver(
            node_hash,
            resolver_address)
        success, tx_receipt, tx_hash = b.send_signed_tx(
            contract_fun, current_owner_key)
        return success, tx_receipt, tx_hash

    def numberSubnodes(self, node_name="root"):
        node_hash = raw_name_to_hash(node_name)
        num = ENS.functions.numberSubnodes(node_hash).call()
        return num

    def subnode(self, node_name="root", index=0):
        node_hash = raw_name_to_hash(node_name)
        subnode = ENS.functions.subnode(node_hash, int(index)).call()
        return subnode

# END: ENS
####################################################
####################################################

####################################################
####################################################
# START: PUBLIC RESOLVER


class PublicResolver_class:

    def __init__(self):
        pass

    def address(self):
        return PublicResolver.address

    def setName(self, node_name="root", name_to_resolve="root", current_owner_key=None):

        if node_name == "root":
            node_hash = b.to_32byte_hex(0)
        else:
            node_hash = raw_name_to_hash(node_name)

        contract_fun = PublicResolver.functions.setName(
            node_hash,
            name_to_resolve)
        success, tx_receipt, tx_hash = b.send_signed_tx(
            contract_fun, current_owner_key)
        return success, tx_receipt, tx_hash

    def name(self, node_name="root", node_hash=None):

        if node_hash is None:
            if node_name == "root":
                node_hash = b.to_32byte_hex(0)
            else:
                node_hash = raw_name_to_hash(node_name)

        name = PublicResolver.functions.name(node_hash).call()

        return name

    def nameFromHash(self, node_hash):

        name = PublicResolver.functions.name(node_hash).call()

        return name

    def setAlaTSP(self, node_name, label, URI, org, active, current_owner_key=None):

        if node_name == "root":
            node_hash = b.to_32byte_hex(0)
        else:
            node_hash = raw_name_to_hash(node_name)

        label_hash = label_to_hash(label)

        contract_fun = PublicResolver.functions.setAlaTSP(
            node_hash,
            label_hash,
            URI,
            org,
            active)
        success, tx_receipt, tx_hash = b.send_signed_tx(
            contract_fun, current_owner_key)
        return success, tx_receipt, tx_hash

    def AlaTSP(self, node_name="root", node_hash=None):

        if node_hash is None:
            if node_name == "root":
                node_hash = b.to_32byte_hex(0)
            else:
                node_hash = raw_name_to_hash(node_name)

        URI, org, active = PublicResolver.functions.AlaTSP(node_hash).call()

        return URI, org, active

    def AlaTSPNumberServices(self, node_name="root", node_hash=None):

        if node_hash is None:
            if node_name == "root":
                node_hash = b.to_32byte_hex(0)
            else:
                node_hash = raw_name_to_hash(node_name)

        numServices = PublicResolver.functions.AlaTSPNumberServices(
            node_hash).call()

        return numServices

    def AlaTSPService(self, node_name="root", node_hash=None, index=0):

        if node_hash is None:
            if node_name == "root":
                node_hash = b.to_32byte_hex(0)
            else:
                node_hash = raw_name_to_hash(node_name)

        X509SKI, serviceName, X509Certificate, active = PublicResolver.functions.AlaTSPService(
            node_hash, index).call()

        return X509SKI, serviceName, X509Certificate, active

    def addAlaTSPService(self, node_name, label, X509SKI, serviceName, X509Certificate, active, current_owner_key=None):

        if node_name == "root":
            node_hash = b.to_32byte_hex(0)
        else:
            node_hash = raw_name_to_hash(node_name)

        label_hash = label_to_hash(label)

        contract_fun = PublicResolver.functions.addAlaTSPService(
            node_hash,
            label_hash,
            X509SKI,
            serviceName,
            X509Certificate,
            active)
        success, tx_receipt, tx_hash = b.send_signed_tx(
            contract_fun, current_owner_key)
        return success, tx_receipt, tx_hash

    def hash(self, text_to_hash):
        return(b.Web3.keccak(text=text_to_hash))

    def setAlaDIDPublicEntity(self, node_name, label, DID, name, DIDDocument, active, new_owner_address, caller_key):

        if node_name == "root":
            node_hash = b.to_32byte_hex(0)
        else:
            node_hash = raw_name_to_hash(node_name)

        label_hash = label_to_hash(label)

        # Calculate the hash of the DID
        DIDHash = b.Web3.keccak(text=DID)

        success, tx_receipt, tx_hash = b.send_signed_tx(
            PublicResolver.functions.setAlaDIDPublicEntity(
                node_hash,
                label_hash,
                DIDHash,
                name,
                DIDDocument,
                active,
                new_owner_address,
            ),
            caller_key
        )

        return success, tx_receipt, tx_hash

    def AlaDIDPublicEntity(self, node_name="root", node_hash=None):

        if node_hash is None:
            if node_name == "root":
                node_hash = b.to_32byte_hex(0)
            else:
                node_hash = raw_name_to_hash(node_name)

        DIDHash, name, DIDDocument, active = PublicResolver.functions.AlaDIDPublicEntity(
            node_hash).call()

        if DIDDocument == "":
            return None, None, None, None

        # Verify integrity: the DIDHash should equal the hash of the DID inside the DIDDocument
        diddoc = json.loads(DIDDocument)
        DID = diddoc["id"]
        did_hash = b.Web3.keccak(text=DID)
        if did_hash == DIDHash:
            return DID, name, DIDDocument, active
        else:
            return None, None, None, None

    def resolveDID(self, _DID: str = None, _DIDHash: HexBytes = None) -> Tuple[str, str, Dict, bool]:

        if _DID is not None:

            # Check that the DID is a string starting with "did:" and that it has some more characters (we accept ANY DID)
            if (not _DID.startswith("did:")) or (len(_DID) <= 4):
                return None, None, None, False

            # Calculate the hash of the DID
            _DIDHash = b.Web3.keccak(text=_DID)

        # Get the node_hash associated to the DID. If the DID is wrong, we get the nil node_hash: bytes32(0)
        node_hash = PublicResolver.functions.nodeFromDID(_DIDHash).call()

        # Get the Entity Data associated to the node.
        DID, name, didDoc, active = self.AlaDIDPublicEntity(
            node_hash=node_hash)

        if didDoc is None:
            return None, None, None, False

        # Convert didDoc to python object
        didDoc = json.loads(didDoc)

        return DID, name, didDoc, active

    def setAlaDIDDocument(self, _DID, DIDDocument, caller_key):

        # Check that the DID is a string starting with "did:" and that it has some more characters (we accept ANY DID)
        if (not _DID.startswith("did:")) or (len(_DID) <= 4):
            return None, None, None, False

        # Calculate the hash of the DID
        _DIDHash = b.Web3.keccak(text=_DID)

        success, tx_receipt, tx_hash = b.send_signed_tx(
            PublicResolver.functions.setAlaDIDDocument(
                _DIDHash,
                DIDDocument
            ),
            caller_key
        )

        return success, tx_receipt, tx_hash

    def setCredential(self, node_name="root",
                      key=None,
                      credentialHash=None,
                      participants=[],
                      caller_key=None):

        if node_name == "root":
            node_hash = b.to_32byte_hex(0)
        else:
            node_hash = raw_name_to_hash(node_name)

        participantsHash = []
        for i in range(5):
            if i < len(participants):
                participantsHash.append(self.hash(participants[i]))
            else:
                participantsHash.append(bytes(32))

        success, tx_receipt, tx_hash = b.send_signed_tx(
            PublicResolver.functions.setCredential(
                node_hash,
                key,
                credentialHash,
                participantsHash[0],
                participantsHash[1],
                participantsHash[2],
                participantsHash[3],
                participantsHash[4],
            ),
            caller_key
        )

        return success, tx_receipt, tx_hash

    def confirmCredential(self, node_name=None, key=None, participantDID=None, caller_key=None):

        if node_name == "root":
            node_hash = b.to_32byte_hex(0)
        else:
            node_hash = raw_name_to_hash(node_name)

        participantHash = self.hash(participantDID)

        success, tx_receipt, tx_hash = b.send_signed_tx(
            PublicResolver.functions.confirmCredential(
                node_hash,
                key,
                participantHash
            ),
            caller_key
        )

        return success, tx_receipt, tx_hash

    def credential(self, node_name=None, key=None):

        if node_name == "root":
            node_hash = b.to_32byte_hex(0)
        else:
            node_hash = raw_name_to_hash(node_name)

        credentialHash, numParticipants = PublicResolver.functions.credential(
            node_hash, key).call()
        return credentialHash, numParticipants

    def credentialParticipant(self, node_name=None, key=None, index=0):

        if node_name == "root":
            node_hash = b.to_32byte_hex(0)
        else:
            node_hash = raw_name_to_hash(node_name)

        DIDhash, signed = PublicResolver.functions.credentialParticipant(
            node_hash, key, index).call()
        return DIDhash, signed


# END: PUBLIC RESOLVER
####################################################
####################################################


####################################################
####################################################
# START: Public Credential
class PublicCredential:

    def __init__(self, node_name=None, key=None, credentialHash=None, participantsDID=[], manager_key=None):

        self.node_name = node_name
        self.key = key
        self.credentialHash = credentialHash
        self.manager_key = manager_key
        self.participants = participantsDID

    def addParticipant(self, DIDHash):
        self.participants.append(DIDHash)

    def createCredential(self, ens, resolver):

        success, _, _ = resolver.setCredential(
            node_name=self.node_name,
            key=self.key,
            credentialHash=self.credentialHash,
            participants=self.participants,
            caller_key=self.manager_key
        )

    def confirmCredential(self, node_name=None, key=None, participantDID=None, caller_key=None):

        success, tx_receipt, tx_hash = resolver.confirmCredential(
            node_name, key, participantDID, caller_key
        )


# END: Public Credential
####################################################
####################################################


#################################################################################
#################################################################################
# Commands called from the MENU
#################################################################################
#################################################################################

def m_compile():
    """Compiles and deploys the Smart Contracts.
    This will forget the currently deployed contracts in the blockchain

    --- Definitions ---
    """
    compile_solidity_file("PublicSelfDeclarations.sol")
    compile_solidity_file("ENSRegistry.sol")
    compile_solidity_file("PublicResolver.sol")


def m_deploy():
    """Compiles and deploys the Smart Contracts.
    This will forget the currently deployed contracts in the blockchain

    --- Definitions ---
    """
    # Create the ROOT account for deployment of the contracts
    print(f"\n==> Creating the root account")
    root_account = wallet.new_account("ROOT", "ThePassword")
    ROOT_address = root_account.address
    ROOT_key = root_account.key
    print(f"Root account created and saved")

    # Deploy the ENS contract using this account
    print(f"\n==> Deploying ENS with root account: {ROOT_address}")
    ENS_address = deploy_ENSRegistry(ROOT_key)
    print(f"ENS deployed at address: {ENS_address}")

    # Deploy the PublicResolver contract, associated to the ENS and with the same root key
    print(f"\n==> Deploying Publicresolver")
    PublicResolver_address = deploy_PublicResolver(ENS_address, ROOT_key)
    print(f"Publicresolver deployed at address: {PublicResolver_address}")

    # Reconnect to the blockchain, this time binding the contracts just deployed
    connect_blockchain()

    # Set the PublicResolver as the resolver of the ROOT node, so it can access all other nodes
    print(f"\n==> Set the PublicResolver as the resolver of the ROOT node")
    ens.setResolver("root", PublicResolver_address, ROOT_key)
    print(f"Done")

    # And assign approval to the PublicResolver contract so it can call ENS methods
    ens.setApprovalForAll(PublicResolver_address, True, ROOT_key)

    # And assign the name "root" to that special root node, to reverse-resolve its name_hash
    print(f"\n==> Assign the name root to the root node, for reverse resolution")
    success, tx_receipt, tx_hash = resolver.setName(
        "root", "root", ROOT_key)
    print(f"Done")


def m_lotl():
    """Re-creates the blockchain ENS nodes with the EU List Of Trusted Lists."""

    # Initialize the contract classes. These classes only work when the smart contracts are already deployed
#    ens = ENS_class()
#    resolver = PublicResolver_class()

    # Get the ROOT account. We need its private key.
    ROOT_address, ROOT_key = wallet.account_from_name("ROOT", "ThePassword")

    # The ROOT account will initially own the whole hierarchy

    # Set the subnode "trust"
    print(f"\n==> Creating the 'trust' subnode")
    success, _, _ = ens.setSubnodeOwner(
        node_name="root",
        label="trust",
        new_owner_address=ROOT_address,
        current_owner_key=ROOT_key
    )
    print(f"'trust' subnode created")

    # Assign the name for reverse resolution of its name_hash
    resolver.setName("trust", "trust", ROOT_key)

    # Set the node "es.trust", representing the Spanish Trusted List
    print(f"\n==> Creating the 'es' (Spanish) subnode")
    success, _, _ = ens.setSubnodeOwner(
        node_name="trust",
        label="es",
        new_owner_address=ROOT_address,
        current_owner_key=ROOT_key
    )
    print(f"'es' subnode created")

    # Assign the name for reverse resolution
    resolver.setName("es.trust", "es.trust", ROOT_key)

    # Now we will create a subnode for each TSP service in Spain
    # For the moment, the owner of those nodes will be the ROOT
    # In the future, ownership will be transferred to the corresponding entities

    # Get the list of TSP services from the DB
    TSPs = get_normalized_TSPs()

    for tsp in TSPs:
        URI = tsp
        URI_clean = URI
        URI_clean = URI_clean.replace("www.", "")
        URI_clean = URI_clean.replace(".com", "")
        URI_clean = URI_clean.replace(".es", "")
        URI_clean = URI_clean.replace(".", "-")

        # Set the sub node depending from node "es.trust"
        print(f"\n==> Creating the '{URI}' subnode of 'es'")
        success, _, _ = ens.setSubnodeOwner(
            node_name="es.trust",
            label=URI_clean,
            new_owner_address=ROOT_address,
            current_owner_key=ROOT_key
        )
        print(f"{URI} subnode created with name: {URI_clean+'.es.trust'}")

        # Assign the name for reverse resolution
        resolver.setName(URI_clean+".es.trust",
                         URI_clean+".es.trust", ROOT_key)

        org = TSPs[tsp][0]["org"]
        print(f"Org: {org}")

        # Set the TSP basic data
        resolver.setAlaTSP(
            node_name="es.trust",
            label=URI_clean,
            URI=URI,
            org=org,
            active=True,
            current_owner_key=ROOT_key
        )

        active = resolver.AlaTSP(node_name=URI_clean+".es.trust")
        print(f"URI: {URI}, Org: {org}, Active: {active}")

        # Now create the services for this TSP
        for service in TSPs[tsp]:

            # Set the service data
            resolver.addAlaTSPService(
                node_name="es.trust",
                label=URI_clean,
                X509SKI=service["X509SKI"],
                serviceName=service["name"],
                X509Certificate=bytes(service["X509Certificate"], "utf-8"),
                active=True,
                current_owner_key=ROOT_key
            )
            print(f"Service: {service['name']}")


def m_lotl_dump():
    """Displays the current Spanish Trusted List from the blockchain."""

    # Initialize the contract classes. These classes only work when the smart contracts are already deployed
#    ens = ENS_class()
#    resolver = PublicResolver_class()

    numberSubnodes = ens.numberSubnodes("es.trust")
    print(f"Number of subnodes: {numberSubnodes}")

    # Iterate for each TSP
    for i in range(ens.numberSubnodes("es.trust")):

        # Get the subnode (in name_hash format)
        tsp_node_hash = ens.subnode("es.trust", i)
        print(f"    Name: {resolver.nameFromHash(tsp_node_hash)}")

        # Get the data for the TSP
        URI, org, active = resolver.AlaTSP(node_hash=tsp_node_hash)
        print(f"    URI: {URI}, Org: {org}, Active: {active}")

        # Get the number of services
        numServices = resolver.AlaTSPNumberServices(node_hash=tsp_node_hash)
        print(f"    Num Services: {numServices}")

        # Iterate all services
        for i in range(numServices):
            X509SKI, serviceName, X509Certificate, active = resolver.AlaTSPService(
                node_hash=tsp_node_hash,
                index=i
            )
            print(f"        X509SKI: {X509SKI}, {serviceName}")


def get_normalized_TSPs():
    """ Get the list of TSPs from the database."""

    db = get_db()

    services = db.execute(
        'SELECT * FROM tl WHERE cc = "es"'
    )

    # The table is de-normalized, so there are several record for TSPs with more than one service
    # Create a normalized structure

    TSPs = {}
    for s in services:
        URI = s["URI"]
        if URI in TSPs:
            TSPs[URI].append(s)
        else:
            TSPs[URI] = [s]

    return TSPs


def m_import_eulotl_db():
    """Import the EU LOTL XML info into the table."""

    print(f"\n==> Erasing and creating the EU LOTL database table")
    reset_eutl_table()
    print(f"EU LOTL database table created")


def m_import_estl_db():
    """Import the Spanish Trusted List XML info into the table."""

    print(f"\n==> Erasing and creating the Spanish Trusted List database table")
    reset_estl_table()
    print(f"Spanish Trusted List database table created")


def create_DID(DID: str, parent_node: str, this_node: str, website: str, commercial_name: str, manager_account):

    # Check if DID already exists
    oldDID, name, oldDidDoc, active = resolver.resolveDID(DID)
    if oldDID is not None:
        print("DID already exists")
        return oldDidDoc

    # Create an external account and save the address and private key.
    # In reality, this should be done by the owner of the identity, and provide only the public key/address
    account_name = DID
    account = wallet.new_account(account_name, "ThePassword", overwrite=False)

    # Initialize the DIDDocument
    didDoc = DIDDocument(
        DID=DID,
        node_name=parent_node,
        label=this_node,
        address=account.address,
        publicKey=account._key_obj.public_key.to_bytes(),
        manager_account=manager_account
    )

    # Add the entity info
    service = {
        "id": DID + "#info",
        "type": "EntityCommercialInfo",
        "serviceEndpoint": website,
        "name": commercial_name
    }
    didDoc.addService(service)

    # Store the info in the blockchain trust framework
    success, tx_receipt, tx_hash = didDoc.createIdentity(ens, resolver)
    if success == False:
        print(tx_receipt)
        return None

    return didDoc


def m_create_test_identities():
    """Create test AlastriaID identities in the Trust Framework hierarchy."""

    # Get the ROOT account (it was created in the deployment of the Smart Contracts)
    ROOT_address, ROOT_key = wallet.account_from_name("ROOT", "ThePassword")

    # Create the Alastria account for node "ala"
    print(f"\n==> Creating the Alastria account")
    Alastria_account = wallet.new_account(
        "Alastria", "ThePassword")
    alakey = Alastria_account.key
    print(f"Alastria key: {alakey}")

    print(f"Done")

    # Set the subnode "ala"
    print(f"\n==> Creating the ala subnode in the Trust Framework")
    success, _, _ = ens.setSubnodeOwner(
        node_name="root",
        label="ala",
        new_owner_address=Alastria_account.address,
        current_owner_key=ROOT_key
    )
    print(f"ala subnode created")

    # Assign the name for reverse resolution
    resolver.setName("ala", "ala", Alastria_account.key)

    # And assign approval to the PublicResolver contract so it can call ENS methods on behalf of Alastria
    print(f"Resolver address for ROOT: {resolver.address()}")
    ens.setApprovalForAll(resolver.address(), True, Alastria_account.key)

    ################################
    # Heathrow airport
    print(f"\n==> Creating the Heathrow identity")

    DID = "did:elsi:VATGB-927365404"
    parent_node = "ala"
    this_node = "heathrow"
    website = "www.heathrow.com"
    commercial_name = "Heathrow Airport Limited"

    didDoc = create_DID(DID, parent_node, this_node, website, commercial_name, Alastria_account)
    if didDoc is not None:
        pprint(didDoc)

    ################################
    # AENA
    print(f"\n==> Creating the AENA identity")

    DID = "did:elsi:VATES-A86212420"
    parent_node = "ala"
    this_node = "aena"
    website = "www.aena.es"
    commercial_name = "Aena"

    didDoc = create_DID(DID, parent_node, this_node, website, commercial_name, Alastria_account)
    if didDoc is not None:
        pprint(didDoc)

    ################################
    # Lanzarote airport
    # The airport belongs to AENA and does not have independent entity (shares the same VAT, for example)
    # In production, the node should be created by AENA, as a subnode controlled by them.
    # In this PoC, the node is created automatically to facilitate the tests
    print(f"\n==> Creating the César Manrique airport identity")

    DID = "did:elsi:VATES-A86212420-1"
    parent_node = "ala"
    this_node = "ace"
    website = "www.aena.es/es/aeropuerto-lanzarote"
    commercial_name = "Aeropuerto de Lanzarote-Cesar Manrique"

    didDoc = create_DID(DID, parent_node, this_node, website, commercial_name, Alastria_account)
    if didDoc is not None:
        pprint(didDoc)

    ################################
    # Metrovacesa
    print(f"\n==> Creating the Metrovacesa identity")

    DID = "did:elsi:VATES-A87471264"
    parent_node = "ala"
    this_node = "metrovacesa"
    website = "metrovacesa.com"
    commercial_name = "Metrovacesa"

    didDoc = create_DID(DID, parent_node, this_node, website, commercial_name, Alastria_account)
    if didDoc is not None:
        pprint(didDoc)

    ################################
    # IN2
    print(f"\n==> Creating the IN2 identity")

    DID = "did:elsi:VATES-B60645900"
    parent_node = "ala"
    this_node = "in2"
    website = "www.in2.es"
    commercial_name = "IN2 Innovating 2gether"

    didDoc = create_DID(DID, parent_node, this_node, website, commercial_name, Alastria_account)
    if didDoc is not None:
        pprint(didDoc)

    ################################
    # BME
    print(f"\n==> Creating the BME identity")

    DID = "did:elsi:VATES-A83246314"
    parent_node = "ala"
    this_node = "bme"
    website = "www.bolsasymercados.es"
    commercial_name = "Bolsas y Mercados Españoles"

    didDoc = create_DID(DID, parent_node, this_node, website, commercial_name, Alastria_account)
    if didDoc is not None:
        pprint(didDoc)


def create_identity(did: str, domain_name: str, website: str, commercial_name: str, parent_node_account: str, password: str):

    # Check that node has at least two components
    s = domain_name.partition(".")
    if len(s[1]) == 0:
        return "Domain name has only one component", None

    this_node = s[0]
    parent_node = s[2]

    # The account name will be the unique domain name
    account_name = did

    # Create an external account and save the address and private key.
    # In reality, this should be done by the owner of the identity, and provide only the public key/address
    account = wallet.create_account(account_name, password, overwrite=False)
    publicKey = PublicKey.from_private(account._key_obj)

    # We assume that the manager account is Alastria, and the password is the one used at creation time
    Manager_account = wallet.get_account(parent_node_account, "ThePassword")
    if Manager_account is None:
        return "Parent node account does not exist", None

    # Initialize the DIDDocument
    didDoc = DIDDocument(
        DID=did,
        node_name=parent_node,
        label=this_node,
        address=account.address,
        publicKey=publicKey,
        manager_account=Manager_account
    )

    # Add the entity info
    service = {
        "id": did + "#info",
        "type": "EntityCommercialInfo",
        "serviceEndpoint": website,
        "name": commercial_name
    }
    didDoc.addService(service)

    # Store the info in the blockchain trust framework
    didDoc.createIdentity(ens, resolver)

    ens.setApprovalForAll(resolver.address(), True, account.key)

    return None, didDoc


def m_create_identity(DID, domain_name, website, commercial_name, parent_node_account, password):
    """Create an identity, with a node name in the Trust Framework and associated DID and address.

    --- Definitions ---
    {"name": "DID", "prompt": "ELSI DID of the new identity", "default": "did:elsi:VATES-B60645900"}
    {"name": "domain_name", "prompt": "Domain name for the new identity", "default": "in2.ala"}
    {"name": "website", "prompt": "Website for the new identity", "default": "www.in2.es"}
    {"name": "commercial_name", "prompt": "Commercial name", "default": "IN2 Innovating 2gether"}
    {"name": "parent_node_account", "prompt": "Account that owns the parent node", "default": "Alastria"}
    {"name": "password", "prompt": "Password to encrypt private key", "default": "ThePassword"}
    """

    error, didDoc = create_identity(
        DID, domain_name, website, commercial_name, parent_node_account, password)
    if error is not None:
        print(error)

    print(f"Created")


def dump_trusted_identities():
    """Returns all Identities in the system depending from the ala node
    """

    node_name = "ala"

    numberSubnodes = ens.numberSubnodes(node_name)
    id_list = []

    # Iterate for each node
    for i in range(numberSubnodes):

        # Get the subnode (in name_hash format)
        subnode_hash = ens.subnode(node_name, i)

        # Get the data for the subnode
        DID, name, DIDDocument, active = resolver.AlaDIDPublicEntity(
            node_hash=subnode_hash)

        identity = {
            "DID": DID,
            "name": name,
            "node_hash": subnode_hash.hex()
        }
        id_list.append(identity)
        
    return id_list

def m_dump_identities(node_name):
    """Displays all Identities in the system.

    --- Definitions ---
    {"name": "node_name", "prompt": "Hierarchical node name", "default": "metrovacesa.deconfianza.ala"}
    """

    numberSubnodes = ens.numberSubnodes(node_name)
    print(f"\n=> Number of subnodes of node {node_name}: {numberSubnodes}")

    # Iterate for each node
    for i in range(numberSubnodes):

        # Get the subnode (in name_hash format)
        subnode_hash = ens.subnode(node_name, i)

        # Get the data for the subnode
        DID, name, DIDDocument, active = resolver.AlaDIDPublicEntity(
            node_hash=subnode_hash)

        print(f"\n    DID: {DID}, Name: {name}")
        print(f"    Node_hash: {subnode_hash.hex()}")


def m_dump_all_identities():
    """Displays all Identities in the system. Assumes they start at the "ala" TLD."""

    m_dump_identities("ala")


def m_create_test_pubcred():
    """Create test Public Credential trust framework."""

    db = get_db()

    # Get the ROOT account (it was created in the deployment of the ENS)
    ROOT_address, ROOT_key = wallet.account_from_name("ROOT", "ThePassword")

    ###############################################
    # Create the Pubcred account for node "pubcred" (address/private key)
    print(f"\n==> Creating the Pubcred account")
    Pubcred_account = wallet.create_and_save_account("Pubcred", "ThePassword")
    print(f"Done")

    # Create subnode "pubcred" and assign ownership to Pubcred address
    print(f"\n==> Creating the pubcred subnode in the Trust Framework")
    success, _, _ = ens.setSubnodeOwner(
        node_name="root",
        label="pubcred",
        new_owner_address=Pubcred_account.address,
        current_owner_key=ROOT_key
    )

    # Authorize the PublicResolver contract to call ENS on behalf of Pubcred
    ens.setApprovalForAll(resolver.address(), True, Pubcred_account.key)

    # Assign the name for easy reverse resolution
    resolver.setName("pubcred", "pubcred", Pubcred_account.key)
    print(f"pubcred subnode created")

    ###################################################################
    # Create the Deconfianza account for node "deconfianza"
    print(f"\n==> Creating the Deconfianza account")
    Deconfianza_account = wallet.create_and_save_account(
        "Deconfianza", "ThePassword")
    print(f"Done")

    # Create subnode "deconfianza.pubcred" and assign ownership to Deconfianza address
    # This is the node at the root of the DECONFIANZA ecosystem
    print(f"\n==> Creating the deconfianza.prubcred subnode in the Trust Framework")
    success, _, _ = ens.setSubnodeOwner(
        node_name="pubcred",
        label="deconfianza",
        new_owner_address=Deconfianza_account.address,
        current_owner_key=Pubcred_account.key
    )

    # Authorize the PublicResolver contract to call ENS on behalf of Deconfianza
    ens.setApprovalForAll(resolver.address(), True, Deconfianza_account.key)

    # Assign the name for reverse resolution
    resolver.setName("deconfianza.pubcred",
                     "deconfianza.pubcred", Deconfianza_account.key)
    print(f"deconfianza.pubcred subnode created")

    ###################################################################
    # Get the Metrovacesa account, that was created as part of the Identity creation
    Metrovacesa_address, Metrovacesa_key = wallet.account_from_name(
        "metrovacesa.ala", "ThePassword")

    # Create subnode "metrovacesa.deconfianza.pubcred" and assign ownership to Metrovacesa
    # Metrovacesa will be able to manage this node and create Public Credentials
    print(f"\n==> Creating the metrovacesa.deconfianza.prubcred subnode in the Trust Framework")
    success, _, _ = ens.setSubnodeOwner(
        node_name="deconfianza.pubcred",
        label="metrovacesa",
        new_owner_address=Metrovacesa_address,
        current_owner_key=Deconfianza_account.key
    )

    # Authorize the PublicResolver contract to call ENS on behalf of Deconfianza
    ens.setApprovalForAll(resolver.address(), True, Metrovacesa_key)

    # Assign the name for reverse resolution
    resolver.setName("metrovacesa.deconfianza.pubcred",
                     "metrovacesa.deconfianza.pubcred", Metrovacesa_key)
    print(f"metrovacesa.deconfianza.pubcred subnode created")

    #####################################
    #####################################
    print(f"\n==> Creating the Public Credential associated to the metrovacesa.deconfianza.prubcred node")
    Metrovacesa_DID = "did:elsi:VATES-A87471264"
    IN2_DID = "did:elsi:VATES-B60645900"
    BME_DID = "did:elsi:VATES-A83246314"

    participants = [
        Metrovacesa_DID,
        IN2_DID,
        BME_DID
    ]

    pubcred = PublicCredential(
        node_name="metrovacesa.deconfianza.pubcred",
        key="Promocion1",
        credentialHash=b"hola",
        participantsDID=participants,
        manager_key=Metrovacesa_key
    )
    # Store the info in the blockchain trust framework
    pubcred.createCredential(ens, resolver)
    print("Created")


def m_credential_create(node_name, credential_hash, participantDID):
    """Creates a credential.

    --- Definitions ---
    {"name": "node_name", "prompt": "Hierarchical node name", "default": "metrovacesa.deconfianza.pubcred"}
    {"name": "credential_hash", "prompt": "Credential hash", "default": "Hola que tal"}
    {"name": "participantDID", "prompt": "Participant DID", "default": "did:elsi:VATES-B60645900"}
    """
    pass


def m_credential_confirm(node_name, key, participantDID, account_name):
    """Creates a credential.

    --- Definitions ---
    {"name": "node_name", "prompt": "Hierarchical node name", "default": "metrovacesa.deconfianza.pubcred"}
    {"name": "key", "prompt": "Unique name of the credential, as a key", "default": "Promocion1"}
    {"name": "participantDID", "prompt": "Participant DID", "default": "did:elsi:VATES-B60645900"}
    {"name": "account_name", "prompt": "Account name", "default": "in2.ala"}
    """
    # Confirm the credential
    acc_address, acc_key = wallet.account_from_name(
        account_name, "ThePassword")
    if acc_address is None:
        print(f"Account {account_name} does not exist")
        return

    print(f"\n==> Confirming the credential by {account_name}")

    try:
        resolver.confirmCredential(
            node_name=node_name,
            key=key,
            participantDID=participantDID,
            caller_key=acc_key
        )
    except ValueError as err:
        print(f"Error: {err}")
    else:
        print("Confirmed!")


def m_credential_display(node_name, key):
    """Displays a credential.

    --- Definitions ---
    {"name": "node_name", "prompt": "Hierarchical node name", "default": "metrovacesa.deconfianza.pubcred"}
    {"name": "key", "prompt": "Unique name of the credential, as a key", "default": "Promocion1"}
    """
    # Confirm the credential

    try:
        credentialHash, numParticipants = resolver.credential(
            node_name=node_name, key=key)
    except ValueError as err:
        print(f"Error: {err}")
        return

    print(f"Credential hash: {credentialHash}")
    print(f"Number of participants: {numParticipants}")

    for i in range(numParticipants):
        DIDHash, signed = resolver.credentialParticipant(
            node_name=node_name, key=key, index=i)
        DID, name, DIDDocument, active = resolver.resolveDID(_DIDHash=DIDHash)

        print(f"\n    DID: {DID}")
        print(f"    Name: {name}")
        print(f"    Signed: {signed}")


def m_get_owner(node_name):
    """Gets the owner of a given node.

    --- Definitions ---
    {"name": "node_name", "prompt": "Hierarchical node name", "default": "metrovacesa.deconfianza.ala"}
    """

    # Initialize the contract classes. These classes only work when the smart contracts are already deployed
#    ens = ENS_class()
#    resolver = PublicResolver_class()

    # Get the owner of the node name
    owner = ens.owner(node_name)
    print(f"Owner address: {owner}")

    # Check if we received the zero address
    if int(owner, base=16) == 0:
        print(f"No owner (or the record is the root record)")
        return

    # Check in the database to see if we have it
    name, pubkey = wallet.account_from_address(owner)
    print(f"Name from the database: {name}")


def m_get_subnode(node_name, index):
    """Gets the subnode at the given index of a specified node.

    --- Definitions ---
    {"name": "node_name", "prompt": "Hierarchical node name", "default": "metrovacesa.deconfianza.ala"}
    {"name": "index", "prompt": "Index of the subnode", "default": "0"}
    """

    # Initialize the contract classes. These classes only work when the smart contracts are already deployed
#    ens = ENS_class()
#    resolver = PublicResolver_class()

    subnode_hash = ens.subnode(node_name, index)

    # Check if we received a cero value (32 bytes will with zeroes)
    if subnode_hash == bytes(32):
        print(f"There are no subnodes")
        return

    # Try to resolve the name from the blockchain
    subnode_name = resolver.name(node_hash=subnode_hash)
    if len(subnode_name) > 0:
        print(
            f"Subnode_hash: {subnode_hash.hex()}, Subnode name: {subnode_name}")
    else:
        print(
            f"Subnode_hash: {subnode_hash.hex()}, could not be resolved to a name.")



def m_get_DIDDocument(DID):
    """Gets the entity data of a given did.

    --- Definitions ---
    {"name": "DID", "prompt": "The DID to resolve", "default": "did:elsi:VATES-A87471264"}
    """

    DID, name, DIDDocument, active = resolver.resolveDID(DID)

    print(f"Name: : {name}")
    print(json.dumps(DIDDocument, ensure_ascii=False, indent=3))


#################################################################################
#################################################################################
# Utilities
#################################################################################
#################################################################################

def connect_blockchain():

    # Connect with the right provider
    b.setup_provider(BLOCKCHAIN_NODE_IP)

    # The path to the contracts deployment artifacts
    ENSRegistry_full_path = os.path.join(CONTRACTS_OUTPUT_DIR, "ENSRegistry")
    PublicResolver_full_path = os.path.join(CONTRACTS_OUTPUT_DIR, "PublicResolver")

    # Bind the ENS and Resolver contracts
    global ENS
    global PublicResolver
    global ens
    global resolver
    ENS = b.bind_contract(ENSRegistry_full_path)
    PublicResolver = b.bind_contract(PublicResolver_full_path)

    # Initialize the high-level contract classes
    ens = ENS_class()
    resolver = PublicResolver_class()

    return ENS, PublicResolver


def deploy_ENSRegistry(root_key: HexBytes):

    ENSRegistry_full_path = os.path.join(CONTRACTS_OUTPUT_DIR, "ENSRegistry")
    print(f"Deploying {ENSRegistry_full_path}")
    success, tx_receipt, ens_address = b.deploy_contract(
        ENSRegistry_full_path,
        private_key=root_key
    )
    if success == False:
        print("Error deploying the contract")
        print(tx_receipt)
        exit(1)

    return ens_address


def deploy_PublicResolver(ENS_address: str, deploy_key: HexBytes):

    PublicResolver_full_path = os.path.join(
        CONTRACTS_OUTPUT_DIR, "PublicResolver")
    print(f"Deploying {PublicResolver_full_path}")
    success, tx_receipt, resolver_address = b.deploy_public_resolver(
        PublicResolver_full_path,
        ens_address=ENS_address,
        private_key=deploy_key
    )
    if success == False:
        print("Error deploying the contract")
        exit(1)

    return resolver_address


def get_db():
    db = sqlite3.connect(DATABASE_NAME, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    return db


def compile_solidity_file(filename):

    # Point to the full path of the file
    sourcefile_path = os.path.join(CONTRACTS_DIR, filename)

    # Create the target directory if it does not exist
    os.makedirs(CONTRACTS_OUTPUT_DIR, exist_ok=True)

    print(f"\n==> Generating ABI for {filename}")
    command_abi = f"solc {sourcefile_path} --evm-version byzantium --abi --overwrite -o {CONTRACTS_OUTPUT_DIR}"
    sp.run(command_abi, shell=True, cwd=SOLC_DIR, text=True, check=True)

    print(f"\n==> Generating BIN for {filename}")
    command_bin = f"solc {sourcefile_path} --evm-version byzantium --bin --overwrite -o {CONTRACTS_OUTPUT_DIR}"
    sp.run(command_bin, shell=True, cwd=SOLC_DIR, text=True, check=True)


def m_setName(node_name="root", name_to_resolve="root", current_owner_alias="ROOT"):
    """Assigns the name to the given record.

    --- Definitions ---
    {"name": "node_name", "prompt": "Node name of the owner of the record?", "default": "root"}
    {"name": "name_to_resolve", "prompt": "Name to assign for reverse resolution", "default": "publicresolver"}
    {"name": "current_owner_alias", "prompt": "Alias of the owner of the key", "default": "ROOT"}
    """

    # Initialize the contract classes. These classes only work when the smart contracts are already deployed
#    ens = ENS_class()
#    resolver = PublicResolver_class()

    # Get the account info from the alias
    account_address, account_key = wallet.account_from_name(
        current_owner_alias, "ThePassword")

    # Set the name
    resolver.setName(node_name, name_to_resolve, account_key)


def m_getName(node_name="root"):
    """Gets the assigned name of the record.

    --- Definitions ---
    {"name": "node_name", "prompt": "Node name of the owner of the record?", "default": "root"}
    """

    # Initialize the contract classes. These classes only work when the smart contracts are already deployed
#    ens = ENS_class()
#    resolver = PublicResolver_class()

    name = resolver.name(node_name=node_name)
    if name == None:
        print("No name assigned")
    else:
        print(f"Name: {name}")

    return name


#################################################################################
#################################################################################
# TRUSTED LISTS MANAGEMENT
#################################################################################
#################################################################################

# Reset the root EU Trusted List table
# Process the XMl file with the information for each country,
# and creates a record in the table with he Country Code and the URL where the list is located
def reset_eutl_table():

    import requests
    from pprint import pprint
    import xml.etree.ElementTree as ET

    import sqlite3

    # Parse the XML file in memory
    eu_lotl_path = os.path.join(TRUSTED_LISTS_DIR, 'eu-lotl.xml')
    tree = ET.parse(eu_lotl_path)
    root = tree.getroot()

    # tl is the dictionary that will hold the trusted list pointer for all countries
    tl = {}
    for c1 in root.iter("{http://uri.etsi.org/02231/v2#}OtherTSLPointer"):
        is_xml = False
        for c2 in c1.iter("{http://uri.etsi.org/02231/v2#}TSLLocation"):
            url = c2.text
            if url.endswith(".xml"):
                is_xml = True
        if is_xml:
            for c2 in c1.iter("{http://uri.etsi.org/02231/v2#}SchemeTerritory"):
                territory = c2.text

            # Create a dict entry with the country code and url
            tl[territory] = url

    # Print the results of parsing
    pprint(tl)
    print("\n")

    # This is the schema for the table
    lotl_schema = """
    DROP TABLE IF EXISTS lotl;

    CREATE TABLE lotl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cc TEXT UNIQUE NOT NULL,
    TSLLocation TEXT UNIQUE NOT NULL
    );
    """

    # Connect to the database and drop (erase) the table
    db = get_db()
    db.executescript(lotl_schema)

    # Insert a record for each entry in the dict
    for cc in tl:
        db.execute(
            'INSERT INTO lotl (cc, TSLLocation) VALUES (?, ?)',
            (cc, tl[cc])
        )
        print(f"Country: {cc}, URL: {tl[cc]}")

    # Save (commit) the changes
    db.commit()
    db.close()


# Reset the Spanish Trusted List. The table will be erased.
# Process the XMl file with the information with the spanish TSPs,
# and create a record in the table
def reset_estl_table():

    # Parse the file with the Spanish Trusted List info
    es_tl_path = os.path.join(TRUSTED_LISTS_DIR, 'es-tl.xml')
    tree = ET.parse(es_tl_path)
    root = tree.getroot()

    # Create a list of dicts, each one with the info for a Qualified Service
    # There may be more than one service entry for a single TSP entity
    # This is OK, as it is the way the Trusted Lists are built
    TSPs = getAllTSPs(root)

    # This is the schema for the table
    # The fields are the following:
    #   cc: Country Code
    #   X509SKI: the SubjectKeyIdentifier field in the X509 certificate identifying the Service/TSP
    #   URI: the URI of the TSP providing the service
    #   org: the organization name, as specified inside the SubjectName field of the certificate
    #   name: the service name
    #   X509SubjectName: the Subjectname field of the certificate
    #   X509Certificate: the full certificate
    tl_schema = """
    DROP TABLE IF EXISTS tl;

    CREATE TABLE tl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    VATID TEXT NOT NULL,
    cc TEXT  NOT NULL,
    X509SKI TEXT UNIQUE NOT NULL,
    URI TEXT NOT NULL,
    org TEXT NOT NULL,
    name TEXT NOT NULL,
    X509SubjectName TEXT NOT NULL,
    X509Certificate TEXT NOT NULL
    );
    """

    # Connect to the database and erase the table
    db = get_db()
    db.executescript(tl_schema)

    # Create a record for each service, even if a TSP provides more than one service.
    # The Country Code is fixed to 'es' (Spain)
    for tsp in TSPs:
        URI = tsp["URI"]
        VATID = tsp["VATID"]
        print(f"ID: {VATID} provides the services:")
        for service in tsp["services"]:
            cc = "es"
            ids = service["ids"]
            X509SKI = ids["X509SKI"]
            org = getOrganizationField(ids["X509SubjectName"])
            name = service["name"]
            X509SubjectName = ids["X509SubjectName"]
            X509Certificate = ids["X509Certificate"]

            print(f"    {URI}: {name}")
            db.execute(
                'INSERT INTO tl (VATID, cc, X509SKI, URI, org, name, X509SubjectName, X509Certificate) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (VATID, cc, X509SKI, URI, org, name,
                 X509SubjectName, X509Certificate)
            )

    # Save (commit) the changes
    db.commit()
    db.close()


ns_prefix = "{http://uri.etsi.org/02231/v2#}"


def ns(tag):
    return ns_prefix + tag


def isServiceTypeQC(srv):
    # The subtag ServiceTypeIdentifier should be http://uri.etsi.org/TrstSvc/Svctype/CA/QC
    srv_type_id = None
    for n in srv.iter(ns("ServiceTypeIdentifier")):
        srv_type_id = n.text
    if srv_type_id == "http://uri.etsi.org/TrstSvc/Svctype/CA/QC":
        return True
    else:
        return False


def isServiceGranted(srv):
    # The subtag ServiceStatus should be http://uri.etsi.org/TrstSvc/TrustedList/Svcstatus/granted
    srv_status = None
    for n in srv.iter(ns("ServiceStatus")):
        srv_status = n.text
    if srv_status == "http://uri.etsi.org/TrstSvc/TrustedList/Svcstatus/granted":
        return True
    else:
        return False


def getServiceName(srv):
    srv_name = None
    for n in srv.iter(ns("ServiceName")):
        # Get the first child contents (supposedly the english one)
        srv_name = n[0].text
    return srv_name


def getServiceDigitalIds(srv):
    digitalIds = {}
    for n in srv.iter(ns("DigitalId")):
        id = n[0].tag.replace(ns_prefix, "")
        value = n[0].text

        if id in digitalIds:
            if digitalIds[id] == value:
                continue
            else:
                print(
                    "WARNING WARNING two digital ids with different values WARNING WARNING WARNING ")
                print(
                    "WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING ")

        digitalIds[id] = value

    return digitalIds


def getOrganizationField(sn):
    ss = sn.split(",")
    for d in ss:
        d = d.strip()
        if d.startswith("O="):
            result = d.replace("O=", "")
            return result


def getAllServices(element):

    # We will create a list of dictionaries, each with individual service data
    all_services = []

    # Search for all TSPService tags
    for srv in element.iter("{http://uri.etsi.org/02231/v2#}TSPService"):

        # We are interested only in Qualified Certificates for Signatures
        if not isServiceTypeQC(srv):
            # Get out from this iteration but continue with the loop
            continue

        # We are interested only in active ("granted") services
        if not isServiceGranted(srv):
            # Get out from this iteration but continue with the loop
            continue

        # Parse the XML and get the relevant data about the service
        name = getServiceName(srv)
        digitalIds = getServiceDigitalIds(srv)

        # Initialize the dictionary
        service = dict(
            name=name,
            ids=digitalIds
        )

        # Add the service to the list
        all_services.append(service)

    return all_services


def get_TSP_URI(srv):
    TSP_URI = None
    for n in srv.iter(ns("TSPInformationURI")):
        # Get the first child contents (supposedly the english one)
        TSP_raw_URI = n[0].text

        # Parse the URI
        parsed_url = urllib.parse.urlparse(TSP_raw_URI)

        # Get the host name (should be a domain name in this case)
        TSP_URI = parsed_url.hostname

        if TSP_URI is None:
            # The URL provided does not follow the syntax specifications in RFC 1808.
            # Just return it unchanged
            TSP_URI = TSP_raw_URI

    return TSP_URI


def get_VATID(srv):
    VATID = None
    for trade_name in srv.iter(ns("TSPTradeName")):
        for name in trade_name:
            if name.text.startswith("VATES-"):
                VATID = name.text
                break
    return VATID


def getAllTSPs(element):

    # We will create a list of dictionaries, each with individual service data
    all_TSPs = []

    # Search for all TrustServiceProvider tags
    for srv in element.iter("{http://uri.etsi.org/02231/v2#}TrustServiceProvider"):

        # For this TSP get its associated hostname address (in TSPInformationURI tag)
        URI = get_TSP_URI(srv)

        # Get the VATES information
        VATID = get_VATID(srv)

        # Get the list of services provided by the TSP
        # The same TSP may provide more than one service
        # Also, we are interested only in Qualified Certificates for Signature,
        # and of those, only in active state ("granted")
        # For this reason, the list may be empty and we skip that TSP
        services = getAllServices(srv)

        if len(services) == 0:
            continue

        # Initialize the dictionary
        TSP_list = dict(
            VATID=VATID,
            URI=URI,
            services=services
        )

        # Add the service to the list
        all_TSPs.append(TSP_list)

    return all_TSPs
