# The Flask web server
from flask import Flask, request, render_template, make_response
from flask import abort, redirect, url_for, jsonify

from blockchain import trustframework as tf
from blockchain import wallet, certificates

# SQLite for storing persistent data
import sqlite3

# A very fast cache with expiration: https://github.com/tkem/cachetools/
from cachetools import TTLCache

# Add CORS support to allow being called from any domain
# This function add the CORS headers to the reply of an OPTIONS reques coming from the browser
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

# This function adds the CORS header to the actual request (POST or GET)
def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response



#####################################################
# CONFIGURE THE SERVER
#####################################################

# Create the app object
app = Flask(__name__)

# Load the configuration from a file
app.config.from_pyfile('app_config.cfg')

# Get the cache config parameters. Default is 10.000 elements where each element expires after 60 seconds
cache_elements = app.config.get("TTLCACHE_NUM_ELEMENTS", 10000)
cache_expiration = app.config.get("TTLCACHE_EXPIRATION", 60)

# Create the cache for messaging credentials
c = TTLCache(cache_elements, cache_expiration)

# Create another cache for DID Documents for 3 hours
doc_cache = TTLCache(100, 3*60*60)

# Connect to blockchain
tf.connect_blockchain()


#####################################################
# MESSAGING SERVER
#####################################################

# Write a payload to the cache associated to a sessionKey
# This API is used to send a Credential to a receiver. It is used by:
# 1. The Issuer when sending a credential to the Passenger
# 2. The Passenger when sending a credential to the Verifier
@app.route('/api/write/<sessionKey>', methods=["POST"])
def write_item(sessionKey):
    
    # Check if we have received some data in the POST
    if request.content_length == 0:
        return {"error": "No data received"}

    # Get the payload as a string
    payload = request.get_data(as_text=True)

    # Store in the cache and return the session key
    c[sessionKey] = payload
    return jsonify({"sessionKey": sessionKey})


# Read the payload from the cache specifying the unique sessionKey
# This API is used to receive a Credential from a sender. It is used by:
# 1. The Issuer when receiving a credential from the Issuer
# 2. The Verifier when receiving a credential from the Passenger
@app.route("/api/read/<sessionKey>", methods=["GET"])
def read_item(sessionKey):

    # Try to get the element from the cache
    element = c.get(sessionKey)
    return jsonify({"payload": element})


#####################################################
# HEALTH CHECKING
#####################################################
@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"payload": "Hello, v1.0.1"})


#####################################################
# VERIFIER APIS
#####################################################

# Resolves a DID and returns the DID Document (JSON format), if it exists
@app.route('/api/did/v1/identifiers/<DID>', methods=["GET"])
def resolve_DID(DID):

    # Check if the DID is already in the cache
    didDoc = doc_cache.get(DID)
    if didDoc is not None:
        return jsonify({"payload": didDoc})
   
    # Try to resolve from the blockchain node
    _DID, name, didDoc, active = tf.resolver.resolveDID(DID)
    if didDoc is None:
        return jsonify({"payload": ""})

    # Store the DID and associated DIDDocument in the cache
    doc_cache[DID] = didDoc

    return jsonify({"payload": didDoc})


#####################################################
# APIS FOR USAGE BY THE VERIFIER MOBILE APP
#####################################################

# Verify a credential, received as a JWT
@app.route('/api/verifiable-credential/v1/verifiable-credential-validations', methods=["POST"])
def credential_verify():

    # Check if we have received some data in the POST
    if request.content_length == 0:
        return {"error": "No data received"}

    # Get the payload as a string
    cert = request.get_data(as_text=True)

    # Verify the certificate
    claims = certificates.verify_cert_token(cert)
    if claims is None:
        print("Verification of token failed")
        return {"error": "Verification of token failed"}

    return jsonify({"payload": claims})



#####################################################
# APIS FOR USAGE BY THE ISSUER MOBILE APP
#####################################################

# Gets a credential (JSON) from issuer by specifying its uniqueID
@app.route('/api/verifiable-credential/v1/<uniqueID>', methods=["GET"])
def credential_get(uniqueID):
    cert = certificates.certificate(uniqueID)
    return jsonify({"payload": cert})

# Get a list (HTML) of credential from the server
@app.route('/api/verifiable-credential/v1/credentials', methods=["GET"])
def credential_list():
    rows = certificates.list_certificates()
    certs = []
    for row in rows:
        certs.append(row["diag_id"])

    return render_template('issuer_credentlal_list.html', credentials=certs)




if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='0.0.0.0', port=8080, debug=True)