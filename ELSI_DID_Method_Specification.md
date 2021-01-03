**Version: 04-06-2020**

<!-- TOC -->autoauto- [1. Introduction](#1-introduction)auto- [2. DID Method Specification for Alastria](#2-did-method-specification-for-alastria)auto    - [2.1. Alastria DID Scheme](#21-alastria-did-scheme)auto    - [2.2. Alastria DID Document specification](#22-alastria-did-document-specification)auto        - [2.2.1. A simple DID document](#221-a-simple-did-document)auto        - [2.2.2. DID Document Context](#222-did-document-context)auto        - [2.2.3. Public keys](#223-public-keys)auto        - [2.2.4. A complete example of an Alastria DID Document](#224-a-complete-example-of-an-alastria-did-document)auto        - [2.2.5. DID Document resolution: from DID to a DID Document](#225-did-document-resolution-from-did-to-a-did-document)auto- [3. Credentials](#3-credentials)auto    - [3.1. Credential Header](#31-credential-header)auto    - [3.2. Credential Payload](#32-credential-payload)auto    - [3.3. Credential Signature](#33-credential-signature)auto    - [3.4. Multiple credentials](#34-multiple-credentials)auto- [4. Presentation](#4-presentation)auto    - [4.1. Presentation header](#41-presentation-header)auto    - [4.2. Presentation payload](#42-presentation-payload)auto    - [4.3. Presentation signature](#43-presentation-signature)auto- [5. Presentation Request](#5-presentation-request)auto    - [5.1. Presentation Request Header](#51-presentation-request-header)auto    - [5.2. Presentation Request Payload](#52-presentation-request-payload)auto    - [5.3. Presentation Request Signature](#53-presentation-request-signature)auto- [6. Private Metadata Sharing and Private Sharing Multi Hashes](#6-private-metadata-sharing-and-private-sharing-multi-hashes)autoauto<!-- /TOC -->

# 1. Introduction

This document has been updated to better align with the latest version of the [W3C Verifiable Credentials Data Model 1.0](https://w3c.github.io/vc-data-model/). 

This document is divided into two parts:

* The first one defines the Alastria DID Method Specification, describing the Alastria DID Scheme and the Alastria DID Document.

* The second part describes the format for Alastria Credentials and Presentations in the current Alastria Red T, based on 
[Quorum](https://github.com/jpmorganchase/quorum).

* The third part describes the Credentials and Presentation Life Cycle and the Private Credential Multi Hashes (PSM Hashes) used to anchor Credential and Presentation actions ensuring privacy. 

The objective of this document is to be aligned with the work on Decentralized IDs (DIDs) and Verifiable Credentials being carried out by the [Verifiable Credentials Working Group](https://www.w3.org/2017/vc/WG/). The specs are already on the CR (Candidate Recommendation) phase and they may still change. However, its maturity is enough to assume that the changes are going to be minor so it makes sense to align the Alastria DID Method Specification as much as possible to those specifications.

The representation format used in this version of the Alastria DID Method Specification is the one referred as JSON-LD with the proof in JWT format in the W3C Verifiable Credentials Data Model 1.0.

# 2. DID Method Specification for Alastria

This is a DID method specification that conforms (with some caveats mentioned explicitly in the text below) to the requirements specified in the [DID specification](https://w3c-ccg.github.io/did-spec/) currently published by the W3C Credentials Community Group. For more information about DIDs and DID method specifications, please see the [DID Primer](https://github.com/WebOfTrustInfo/rebooting-the-web-of-trust-fall2017/blob/master/topics-and-advance-readings/did-primer.md).

Alastria is technology-agnostic, and the first implementation of the blockchain network is using Quorum. However, it is envisioned that more technologies are going to be used in parallel (like [Hyperledger Fabric](https://github.com/hyperledger/fabric)), so the requirement is to define an identification system that is as interoperable as possible across blockchain implementations.

As described in the [DID specification](https://w3c-ccg.github.io/did-spec/),

> "A DID MUST be persistent and immutable, i.e., bound to an entity once and never changed (forever). **Ideally a DID would be a completely abstract decentralized identifier (like a UUID) that could be bound to multiple underlying distributed ledgers or networks over time**, thus maintaining its persistence independent of any particular ledger or network. However registering the same identifier on multiple ledgers or networks introduces extremely hard entityship and start-of-authority (SOA) problems. It also greatly increases implementation complexity for developers.
>
> To avoid these issues, it is RECOMMENDED that DID method specifications only produce DIDs and DID methods bound to strong, stable ledgers or networks capable of making the highest level of commitment to persistence of the DID and DID method over time.
>
> NOTE: Although not included in this version, **future versions of this specification may support a DID Document equivID property to establish verifiable equivalence relations between DID records representing the same identifier** owner on multiple ledgers or networks. Such equivalence relations can produce the practical equivalent of a single persistent abstract DID."

The approach in Alastria is twofold:

1. On one hand, the Alastria DID format includes the type of network in the DID so resolvers can use this to access the proper network for DID document resolution.

2. On the other hand, Alastria will include an early implementation of the suggested "**equivID**" property, as soon as there is another blockchain network.

## 2.1. Alastria DID Scheme

Alastria DIDs have the following format:

```
did                = "did:ala:" network ":" specific-idstring

network            = ("quor" / "fabr") ":" net-id

specific-idstring  = depends on the network, see below
```

The components specific to the Alastria DID are the following:

* **"ala"**: specifies that this is a DID for Alastria.

* **network**: specifies the underlying technology for the specific Alastria network. The mechanisms and algorithms used to resolve and manage DID documents can be very different across technologies, so this component tells application developers what algorithm to use for a given DID instance. The current value for this component is "**quor**" for the Quorum-based networks, but it is expected that a network using “**fabr**” will be added soon. Other values will be added as Alastria ID is implemented on top of other technologies.

* **net-id**: defines the specific Alastria blockchain network instance. Currently the only value accepted is "**testnet1**".

Example DIDs can be:

For the current Red T, based on Quorum:

**_"did:ala:quor:redt:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1"_**

For a possible Hyperledger Fabric testnet:

**_"did:ala:fabr:testnet5:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1"_**

For the current Red T network, "*specific-idstring*" is the **Ethereum address of the Proxy Contract representing the Alastria.ID of the entity, coded in Hex without 0x prefix**. The creation of a Proxy Contract is specified in the Alastria.ID specification documents. For the future Fabric network, it is still under definition.

The next sections describe the DID Method Specification for the current Quorum implementation.

## 2.2. Alastria DID Document specification

If we think of a DID as the index key in a key-value pair, then the DID Document is the value to which the index key points. The combination of a DID and its associated DID Document forms the root record for a decentralized identifier.

A DID Document is a single JSON object conforming to [RFC7159](https://tools.ietf.org/html/rfc7159). In Alastria, the instance of the DID Document associated to a specific DID does not have to exist in a physical storage system, but it is in reality "virtual". This means that given a DID, there is a procedure to construct a DID Document with all the information related to the associated basic Alastria.ID as per the [DID specification](https://w3c-ccg.github.io/did-spec/). The DID Document does not contain any information related to the attestations or claim presentations associated to the ID.

### 2.2.1. A simple DID document

A simple DID document has the following structure:

```javascript
{
  "@context": "https://w3id.org/did/v1",
  "id": "did:ala:quor:redt:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1",
  "publicKey": [{ ... }],
  "authentication": [{ ... }],
  "service": [{ ... }]
}
```


For the moment, in Alastria we will not use the "**authentication**" and “**service**” sections.

### 2.2.2. DID Document Context

As per the  [DID specification](https://w3c-ccg.github.io/did-spec/), Alastria will use the context defined here: [https://w3id.org/did/v1](https://w3id.org/did/v1):

```javascript
"@context": "https://w3id.org/did/v1"
```

### 2.2.3. Public keys

The keys associated to the Alastria.ID in the Quorum implementation have to be generated according to the Ethereum specifications. In the current version of the DID specification "[Decentralized Identifiers (DIDs) v0.11](https://w3c-ccg.github.io/did-spec/)" such keys are not yet supported, so we have to define a new key type.

The suggested name is "**_EcdsaKoblitzPublicKey_**" given that Bitcoin and Ethereum use the Koblitz Elliptic Curve, also known as *secp256k1*. This is also consistent with the upcoming definition of a new Signature Suite in the Verifiable Credentials Data Model, called “**_EcdsaKoblitzSignature2016_**”.

An example publicKey entry in the DID Document, with a single key, could be:

```javascript
...
"publicKey": [{
    "id": "did:ala:quor:testnet1:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1#keys-1",
    "type": ["CryptographicKey", "EcdsaKoblitzPublicKey"],
    "curve": "secp256k1",
    "expires": "2019-06-11T22:07:10Z",
    "publicKeyHex": "0xf42987b7faee8b95e2c3a3345224f00e00dfc67ba88266b35efd6fc481e162b7f3471617b2433cdc74d04c81ef6db911ca416efa296cd2c4962e35d804560104"
}],
...
```

The "id" of the “publicKey” has two components:

1. "**did:ala:quor:testnet1:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1**" is the DID for the owner of the key, which is the DID subject.

2. "**#keys-1**" is a URI fragment which specifies the specific key from the DID subject. For the moment, an Alastria.ID has only one key, but this is the generic mechanism in the DID specification to identify several keys for several purposes. In order to achieve forward compatibility, it is recommended to use a URI fragment to identify the key, even though currently is not strictly necessary.

### 2.2.4. A complete example of an Alastria DID Document

```javascript
{
  "@context": "https://w3id.org/did/v1",
  "id": "did:ala:quor:testnet1:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1",
  "publicKey": [{
    "id": "did:ala:quor:testnet1:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1#keys-1",
    "type": ["CryptographicKey", "EcdsaKoblitzPublicKey"],
    "curve": "secp256k1",
    "expires": "2019-06-11T22:07:10Z",
    "publicKeyHex": "0xf42987b7faee8b95e2c3a3345224f00e00dfc67ba88266b35efd6fc481e162b7f3471617b2433cdc74d04c81ef6db911ca416efa296cd2c4962e35d804560104"
  }],
}
```


### 2.2.5. DID Document resolution: from DID to a DID Document

The DID Document resolution process describes how to obtain the DID Document associated to a given DID.

In Alastria, the process is basically the following:

1. From the DID, determine the type of network (Quorum or Fabric), and the specific instance (Testnet1, for example).

2. Use the DID to obtain the associated public key using the "**AlastriaPublicKeyRegistry**" Smart Contract.

3. Create the DID Document.

# 3. Credentials

In this document, we are going to describe only the aspects which are specific to the Alastria implementation of the standard Credential and Presentation model, to clarify those aspects to the implementers willing to maintain a high level of interoperability with all the other implementations in the ecosystem.
For the detailed description of the model, please refer to the [W3C Verifiable Credentials Data Model 1.0](https://w3c.github.io/vc-data-model/) document.

For simplicity, we will use simply the term Credential to refer to a Verifiable Credential, as these are the only ones being useful in the context of Alastria ID. In order to make credentials easily manageable in Alastria, we are currently representing the credentials in the format named JSON-LD+JWTs in the [Verifiable Credentials Implementation Guidelines 1.0](https://w3c.github.io/vc-imp-guide/)) document.

This means that we will use the JSON Web Token format to represent a Credential. A JWT token consists of three parts: Header, Payload and Signature.

## 3.1. Credential Header

The header part has two mandatory fields:

* **"typ"** which is the type of the format (always "JWT")

* **"alg"** which is the signature scheme employed (always "ES256K"). A list of defined "**alg**" values can be found in the IANA [JSON Web Signature and Encryption Algorithms (JWA)](https://tools.ietf.org/html/rfc7518) registry.
However, the currently defined schemes are not compatible with Ethereum keys and signature procedures. The most similar one would be the "**ES256**", which is a signature suite that uses the elliptic curve defined by NIST P-256, aka *secp256r1* or *prime256v1*. In contrast, Bitcoin and Ethereum use the *secp256k1* curve.
There is however an [IETF draft proposal](https://tools.ietf.org/html/draft-jones-webauthn-secp256k1-00) to include a signature scheme using the *secp256k1* curve, and this is the recommended signature scheme to use in the Alastria Credentials represented as JWT tokens.
The proposed signature name (already registered in IANA) is "**ES256K**" which is the name used in the example header above.

And two optional fields:

* **"kid"** which is the id of the public key. This parameter indicates which key was used to secure (digitally sign) the JWT. In Alastria, the value of the “kid” is the DID reference of the public key as it appears in the DID Document associated to the Alastria ID of the issuer of the Credential. So it always should follow the pattern: ```did + "#" + key alias```

* **"jwk"** is the public key which was used to sign the JWT. It has hex format so it should start with ```0x``` It is optional because in the current implementation, public keys are registered in a Smart Contract.

```javascript
{
    "alg": "ES256K",
    "typ": "JWT",
    "kid": "did:ala:quor:redt:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1#keys-1",
    "jwk": "0x2e507af01167c98a6accc0cd46ab2a256dd6b6c69ec1c0c28f80fb62e1f7d70233768b0c58dbbdac1fc358b8141c075a520483cf9779e4ea98d13df2833f3767"
}
```

## 3.2. Credential Payload

The credential data and meta-data is encoded as a JSON object that is used as the payload of the JWT.

An example payload for a credential of the name of a natural person is the following:

```javascript
{
  "jti": "https://www.oneweb.com/alastria/credentials/3732",
  "iss": "did:alastria:quorum:redt:c5039eae214608fc5039eae2146083cdc42a87aeeacf848efb9924a381ccb5d1",
  "sub": "did:alastria:quorum:redt:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1",
  "iat": 1525465044,
  "exp": 1530735444,
  "nbf": 1525465044,
  "vc": {
    "@context": [
      "https://www.w3.org/2018/credentials/v1",
      "https://alastria.github.io/identity/credentials/v1",
      "https://universities.io/examples/v1"
    ],
    "type": ["VerifiableCredential","AlastriaVerifiableCredential", "UniversityDegreeCredential"],
    "credentialSubject": {
      "levelOfAssurance": 0,
      "degree": {
        "type": "BachelorDegree",
        "name": "Bachelor of Science and Arts"
      }
    }
  }
}
```

Note: the field **"nonce"** is not needed because in Alastria **"iat"** is compulsory, acting effectively as a nonce.

The following is a brief description of the fields in the example credential:

* **"jti"** (JWT ID, or “id” in the VC spec): [OPTIONAL] This is the identification of this specific credential (it is NOT the identifier of the holder or of any other actor). The requirement is that it is a unique identifier for all possible credentials.

    The identifier value MUST be assigned in a manner that ensures that there is a negligible probability that the same value will be accidentally assigned to a different credential. Collisions MUST be prevented among values produced by different issuers. It could be a simple hash (making sure to include some fields which are unique globally, like a nonce), or it could be formatted as an URI, but not necessarily storing the actual credential data at that URI (to take care of data privacy, as the credential may contain PII or other sensitive data).  

    The "jti" claim can be used to prevent the JWT from being replayed, as mentioned in section 4.1.7 of the [JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519#section-4.1.7) specification

* **"iss"** (“issuer” in the VC spec): [REQUIRED] The value of this property is a DID representing the AlastriaID of the entity that issued the credential. Dereferencing the DID results in a document containing machine-readable information about the issuer that may be used to verify the information expressed in the credential.

* **"sub"**: [OPTIONAL] The DID representing the AlastriaID of the subject to which the credential refers to.

* **"iat"** (Issued at): [REQUIRED] Identifies the time at which the JWT (that is, the credential) was issued. This field can be used to determine the age of the credential.  Its value MUST be a number containing a NumericDate value.

    A **NumericDate** value is a JSON numeric value representing the number of seconds from 1970-01-01T00:00:00Z UTC until the specified UTC date/time, ignoring leap seconds. This is equivalent to the IEEE Std 1003.1,  2013 Edition [POSIX.1] definition "Seconds Since the Epoch", in which each day is accounted for by exactly 86400 seconds, other than that non-integer values can be represented.  See RFC 3339 [RFC3339] for details regarding date/times in general and UTC in particular.

* **"exp"** (Expiration time): [OPTIONAL] The "exp" (expiration time) field identifies the expiration time on or after which the JWT (credential) MUST NOT be accepted for processing.  The processing of the "exp" field requires that the current date/time MUST be before the expiration date/time listed in the "exp" field.

    Implementers MAY provide for some small leeway, usually no more than a few minutes, to account for clock skew.  Its value MUST be a number containing a NumericDate value.

* "**nbf**" (Not Before): [OPTIONAL] The "nbf" (not before) field identifies the time before which the JWT (credential) MUST NOT be accepted for processing. The processing of the "nbf" field requires that the current date/time MUST be after or equal to the not-before date/time listed in the "nbf" field. Implementers MAY provide for some small leeway, usually no more than a few minutes, to account for clock skew.  Its value MUST be a number containing a NumericDate value.

* **"vc"**: [REQUIRED] It is the structure that contains the actual credential data.

    *  **"@context"**: [REQUIRED] The context will be an array with https://alastria.github.io/identity/credentials/v1 and also the own of W3C https://www.w3.org/2018/credentials/v1. You can add more additional urls but these two will be compulsory.
    * "**type**": [REQUIRED] The type will be an array with "VerifiableCredential",  "AlastriaVerifiableCredential". More additional types can be added but these two will be mandatory.

    * **"levelOfAssurance"**: [OPTIONAL] Corresponds to the eIDAS assurance levels ("Self", “Low”, “Substantial”, “High”), plus an additional lower level “Self” for self-asserted data. The actual level depends on the entity making the credential and the process used by the entity to verify the attribute. If the field does not exist in the credential, the verifier will have to use the knowledge that it has about the issuing entity in order to assess the risks associating with accepting that credential.

    * The rest of the fields correspond to the standard claim names in JWT.

In order to improve the granularity available to subjects when presenting credentials to service providers, it is recommended that credentials be generated without aggregating several attributes in the same credential. In this way, the subject will have more freedom to select which credentials will be presented to the service provider, and minimize the data exposed and which is not strictly required.

Two more examples of credentials follow, one for the email address and the second for a phone number. They will be used later in the example of presentation of several credentials to a service provider.

Note that the "**jti**" fields are different, identifying different credentials.

```javascript
{
  "jti": "https://www.oneweb.com/alastria/credentials/3733",
  "iss": "did:alastria:quorum:redt:5039eae2146083cd9eae21851fc5039eae2112355848efb9924a381cc4b2b5d1",
  "sub": "did:alastria:quorum:redt:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1",
  "iat": 1525465044,
  "exp": 1530735444,
  "nbf": 1525465044,
  "vc": {
    "@context": [
      "https://www.w3.org/2018/credentials/v1",
      "https://alastria.github.io/identity/credentials/v1",
      "https://alastria.github.io/identity/covid"
    ],
    "type": ["VerifiableCredential", "AlastriaVerifiableCredential", "CovidTestCredential"],
    "credentialSubject": {
      "levelOfAssurance": 3,
      "covid_test": {
           "name": "Perico Perez"
           "mail": "perico.perez@example.com"
           "test_result": "negative"
           ...
      }
    }
  }
}
```

```javascript
{
  "jti": "https://www.oneweb.com/alastria/credentials/3734",
  "iss": "did:alastria:quorum:redt:c53a53a851fc5039eae21460cdc42a87aeeacf848efb9eae21a381cc4b2b",
  "sub": "did:alastria:quorum:redt:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1",
  "iat": 1525465044,
  "exp": 1530735444,
  "nbf": 1525465044,
  "vc": {
    "@context": [
      "https://www.w3.org/2018/credentials/v1",
      "https://alastria.github.io/identity/credentials/v1",
      "https://alastria.github.io/identity/examples/v1"
    ],
    "type": ["VerifiableCredential", "AlastriaVerifiableCredential", "AlastriaExamplePhoneCredential"],
    "credentialSubject": {
      "levelOfAssurance": 0,
      "phone_number": "+34999999999",
    }
  }
}
```

## 3.3. Credential Signature

The signature part is computed according to the JWS specification, without any modification or extension.

## 3.4. Multiple credentials

When an issuer needs to send multiple credentials to a user, those can be send as a JSON array named "verifiableCredential" whose elements are serialized credentials (line-breaks added in the example to enhance readability).

Example:

```
{
  verifiableCredential: [
'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksiLCJraWQiOiJkaWQ6YWxhOnF1b3I6cmVkVDo4ZjQ0MDA0O
WNiYmU1YzZiYzllZmY0NjM2OWY5MDkxZjFkODEzMzNjI2tleXMtMSJ9.
eyJqdGkiOiJmaGJ0aDlocnVkbCIsImlzcyI6ImRpZDphbGE6cXVvcjpyZWRUOjhmNDQwMDQ5Y2JiZTVjNmJjOW
VmZjQ2MzY5ZjkwOTFmMWQ4MTMzM2MiLCJzdWIiOiJkaWQ6YWxhOnF1b3I6cmVkVDowYTc3ODAyOTVhYjgwNmY4
Y2RiNjIzY2ZhNDhhNzQ5ZTk1OTE4MTU5IiwiaWF0IjoxNTkxMTczNjkzLCJleHAiOjE1OTEyNjAwOTMxNDMsIm
5iZiI6MTU5MTE3MzY5MzE0MywidmMiOnsiQGNvbnRleHQiOlsiaHR0cHM6Ly93d3cudzMub3JnLzIwMTgvY3Jl
ZGVudGlhbHMvdjEiLCJKV1QiXSwidHlwZSI6WyJWZXJpZmlhYmxlQ3JlZGVudGlhbCIsIkFsYXN0cmlhRXhhbX
BsZUNyZWRlbnRpYWwiXSwiY3JlZGVudGlhbFN1YmplY3QiOnsibGV2ZWxPZkFzc3VyYW5jZSI6MywiZnVsbG5h
bWUiOiJEYW5pZWwgZGUgbGEgU290YSJ9fX0.
DZsssNSg0_NzrjSiCNrkVss9-bnUZxFrbH6oN9NluCJwg0MqwAvyvwtKww_f_lF1sMVXt6UZyl_gJEkCSaspWw',
'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksiLCJraWQiOiJkaWQ6YWxhOnF1b3I6cmVkVDo4ZjQ0MDA0OWNiY
mU1YzZiYzllZmY0NjM2OWY5MDkxZjFkODEzMzNjI2tleXMtMSJ9.
eyJqdGkiOiJ6Mnlkandjcnh0IiwiaXNzIjoiZGlkOmFsYTpxdW9yOnJlZFQ6OGY0NDAwNDljYmJlNWM2YmM5ZW
ZmNDYzNjlmOTA5MWYxZDgxMzMzYyIsInN1YiI6ImRpZDphbGE6cXVvcjpyZWRUOjBhNzc4MDI5NWFiODA2Zjhj
ZGI2MjNjZmE0OGE3NDllOTU5MTgxNTkiLCJpYXQiOjE1OTExMTI5OTIsImV4cCI6MTU5MTE5OTM5MjQxNiwibm
JmIjoxNTkxMTEyOTkyNDE2LCJ2YyI6eyJAY29udGV4dCI6WyJodHRwczovL3d3dy53My5vcmcvMjAxOC9jcmVk
ZW50aWFscy92MSIsIkpXVCJdLCJ0eXBlIjpbIlZlcmlmaWFibGVDcmVkZW50aWFsIiwiQWxhc3RyaWFFeGFtcG
xlQ3JlZGVudGlhbCJdLCJjcmVkZW50aWFsU3ViamVjdCI6eyJsZXZlbE9mQXNzdXJhbmNlIjozLCJmdWxsbmFt
ZSI6IkRhbmllbCBkZSBsYSBTb3RhIn19fQ.
vh8aJ9ohkeeKkhuD5ctDkZdyjhsgpY_z1YLzBF0JqDz0O8jmBQvqBsIvSLAKp4O2VM8E7yQ9XDRGb2uzMjHCnQ'
  ]
}
```


# 4. Presentation

A presentation object is a collection of one or more credentials that have been issued by one or multiple issuers. The aggregation of this information typically expresses an aspect of a person, organization, or entity.

As described before, a verifiable credential is a JWT signed by the issuer of the credential, which means that the data is *base64url* encoded.

The Presentation is also a signed JWT (signed by the subject presenting the claims), containing in its payload the collection of one or more credentials, in addition to some additional data specific to the Presentation.

## 4.1. Presentation header

The header part has two mandatory fields:

* **"typ"** which is the type of the format (always "JWT")

* **"alg"** which is the signature scheme employed (always "ES256K"). A list of defined "**alg**" values can be found in the IANA [JSON Web Signature and Encryption Algorithms (JWA)](https://tools.ietf.org/html/rfc7518) registry.
However, the currently defined schemes are not compatible with Ethereum keys and signature procedures. The most similar one would be the "**ES256**", which is a signature suite that uses the elliptic curve defined by NIST P-256, aka *secp256r1* or *prime256v1*. In contrast, Bitcoin and Ethereum use the *secp256k1* curve.
There is however an [IETF draft proposal](https://tools.ietf.org/html/draft-jones-webauthn-secp256k1-00) to include a signature scheme using the *secp256k1* curve, and this is the recommended signature scheme to use in the Alastria Credentials represented as JWT tokens.
The proposed signature name (already registered in IANA) is "**ES256K**" which is the name used in the example header above.

And two optional fields:

* **"kid"** which is the id of the public key. This parameter indicates which key was used to secure (digitally sign) the JWT. In Alastria, the value of the “kid” is the DID reference of the public key as it appears in the DID Document associated to the Alastria ID of the issuer of the Credential. So it always should follow the pattern: ```did + "#" + key alias```

* **"jwk"** is the public key which was used to sign the JWT. It has hex format so it should start with ```0x``` It is optional because in the current implementation, public keys are registered in a Smart Contract.

```javascript
{
    "alg": "ES256K",
    "typ": "JWT",
    "kid": "did:ala:quor:redt:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1#keys-1",
"jwk": "0x2e507af01167c98a6accc0cd46ab2a256dd6b6c69ec1c0c28f80fb62e1f7d70233768b0c58dbbdac1fc358b8141c075a520483cf9779e4ea98d13df2833f3767"
}
```


## 4.2. Presentation payload

Many of the fields in the JWT payload of a presentation are the same as in a verifiable credential. We will use an example presentation to describe the contents.

```javascript
{
  "jti": "https://www.empresa.com/alastria/credentials/3732",
  "iss": "did:alastria:quorum:redt:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1",
  "aud": "did:alastria:quorum:redt:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1",
  "iat": 1525465044,
  "exp": 1530735444,
  "nbf": 1525465044,
  "vp": {
    "@context": [
      "https://www.w3.org/2018/credentials/v1",
      "https://alastria.github.io/identity/credentials/v1",
    ],
    "type": ["VerifiablePresentation", "AlastriaVerifiablePresentation"],
    "procHash": "H398sjHd...kldjUYn475n",
    "procUrl": "https://www.empresa.com/alastria/businessprocess/4583",
    // base64url-encoded JWT as string
    "verifiableCredential": [{ ... }]
  }

}
```

The following is a brief description of the fields in the example Presentation:

* **"jti"** (JWT ID, or “id” in the VC spec): [OPTIONAL] This is the identification of this specific presentation instance (it is NOT the identifier of the holder or of any other actor). The same requirements for uniqueness apply as for the “**jti**” field of credentials.

* **"iss"** (Issuer): [REQUIRED] The value of this property is a DID representing the Alastria.ID of the entity that issued the presentation (normally the citizen). Dereferencing the DID results in a document containing machine-readable information about the issuer that may be used to verify the information expressed in the presentation.

* **"aud"** (Audience): [REQUIRED] The "aud" (audience) field identifies the recipient that the JWT is intended for. The principal intended to process the JWT MUST identify itself with a value in the audience field. In Alastria, the value of “aud” is the DID representing the Alastria.ID of the entity receiving the presentation.

* **"iat"** (Issued at): [REQUIRED] Identifies the time at which the JWT (that is, the presentation) was issued. This field can be used to determine the age of the presentation.  Its value MUST be a number containing a NumericDate value.

* **"exp"** (Expiration time): [OPTIONAL] The "exp" (expiration time) field identifies the expiration time on or after which the JWT (presentation) MUST NOT be accepted for processing.  The processing of the "exp" field requires that the current date/time MUST be before the expiration date/time listed in the "exp" field.

    Implementers MAY provide for some small leeway, usually no more than a few minutes, to account for clock skew.  Its value MUST be a number containing a NumericDate value.

* "**nbf**" (Not Before): [OPTIONAL] The "nbf" (not before) field identifies the time before which the JWT (presentation) MUST NOT be accepted for processing. The processing of the "nbf" field requires that the current date/time MUST be after or equal to the not-before date/time listed in the "nbf" field. Implementers MAY provide for some small leeway, usually no more than a few minutes, to account for clock skew.  Its value MUST be a number containing a NumericDate value.

* **"vp"**: [REQUIRED] It is the structure that contains the actual presentation data.

    *  **"@context"**: [REQUIRED] The context will be an array with https://alastria.github.io/identity/credentials/v1 and also the own of W3C https://www.w3.org/2018/credentials/v1. You can add more additional urls but these two will be compulsory.
    * "**type**": [REQUIRED] The type will be an array with "VerifiablePresentation",  "AlastriaVerifiablePresentation". More additional types can be added but these two will be mandatory.
    * "**procHash**" (Process Hash): [REQUIRED] The hash of an external document describing the intended purpose of the data that the service provider is receiving. This hash links the presentation to a specific Business Process Name & Description.
    *  "**procUrl**" (Process URL): [REQUIRED] The URL of an external document describing the intended purpose of the data that the service provider is receiving.
    *  **"verifiableCredential"**: [REQUIRED] An array of verifiable credentials in JWT format, that is, signed JWTs where each verifiable credential is base64url encoded.

## 4.3. Presentation signature

The signature part is computed according to the JWS specification, without any modification or extension.

# 5. Presentation Request

This is a process which is not included in the [W3C Verifiable Credentials Data Model 1.0](https://w3c.github.io/vc-data-model/) document, which as its name indicates, describes just the data model.

In Alastria, a Presentation Request object is a collection of one or more data items which the service provider is asking from a subject.
The entity receiving the Presentation Request (normally the subject) uses it to create an appropriate Presentation object that satisfies the requirements from the service provider.

The Presentation Request is a signed JWT (signed by the entity sending the request), containing in its payload the collection of one or more data items and the required LoA (Level of Assurance).

## 5.1. Presentation Request Header

The header part has two mandatory fields:

* **"typ"** which is the type of the format (always "JWT")

* **"alg"** which is the signature scheme employed (always "ES256K"). A list of defined "**alg**" values can be found in the IANA [JSON Web Signature and Encryption Algorithms (JWA)](https://tools.ietf.org/html/rfc7518) registry.
However, the currently defined schemes are not compatible with Ethereum keys and signature procedures. The most similar one would be the "**ES256**", which is a signature suite that uses the elliptic curve defined by NIST P-256, aka *secp256r1* or *prime256v1*. In contrast, Bitcoin and Ethereum use the *secp256k1* curve.
There is however an [IETF draft proposal](https://tools.ietf.org/html/draft-jones-webauthn-secp256k1-00) to include a signature scheme using the *secp256k1* curve, and this is the recommended signature scheme to use in the Alastria Credentials represented as JWT tokens.
The proposed signature name (already registered in IANA) is "**ES256K**" which is the name used in the example header above.

And two optional fields:

* **"kid"** which is the id of the public key. This parameter indicates which key was used to secure (digitally sign) the JWT. In Alastria, the value of the “kid” is the DID reference of the public key as it appears in the DID Document associated to the Alastria ID of the issuer of the Credential. So it always should follow the pattern: ```did + "#" + key alias```

* **"jwk"** is the public key which was used to sign the JWT. It has hex format so it should start with ```0x``` It is optional because in the current implementation, public keys are registered in a Smart Contract.

```javascript
{
    "alg": "ES256K",
    "typ": "JWT",
    "kid": "did:ala:quor:redt:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1#keys-1",
"jwk": "0x2e507af01167c98a6accc0cd46ab2a256dd6b6c69ec1c0c28f80fb62e1f7d70233768b0c58dbbdac1fc358b8141c075a520483cf9779e4ea98d13df2833f3767"
}
```


## 5.2. Presentation Request Payload

The Presentation Request data and metadata is encoded as a JSON object that is used as the payload of the JWT.

We are going to use an example payload for a Presentation Request to explain its format:

```javascript
{
  "jti": "metrovacesa/alastria/presentationrequest/7864",
  "iss": "did:alastria:quorum:testnet1:3eabc53a851fc5039eae2146083cdc42a87aeeacf848efb9924a381cc4b2b5d1",
  "iat": 1525465044,
  "exp": 1530735444,
  "nbf": 1525465044,
  "cbu": "https://www.metrovacesa.com/alastria/presentation?jtipr=7864"

  "pr": {
    "@context": [
      "https://www.w3.org/2018/credentials/v1",
      "https://alastria.github.io/identity/credentials/v1"
    ],
    "type": ["VerifiablePresentationRequest", "AlastriaVerifiablePresentationRequest"],
    "procHash": "H398sjHd...kldjUYn475n",
    "procUrl": "https://www.example-company.com/alastria/businessprocess/4583",
    "data": [
      {
        "@context": ["https://alastria.github.io/identity/covid/v1"],
        "levelOfAssurance": 3,
        "required": true,
        "field_name": "covid_test",
      },
      {
        "@context": ["https://alastria.github.io/identity/examples/v1"],
        "levelOfAssurance": 2,
        "required": true,
        "field_name": "phone_number",
      }
    ],
  }
```


The following is a brief description of the fields in the example Presentation Request:

* **"jti"** (JWT ID, or “id” in the VC spec): [OPTIONAL] This is the identification of this specific Presentation Request (it is NOT the identifier of the holder or of any other actor). The requirement is that it is a unique identifier for all possible Presentation Requests. In this example it is formatted as an URL, but it could be any unique identifier:

    The identifier value MUST be assigned in a manner that ensures that there is a negligible probability that the same value will be accidentally assigned to a different Presentation Request. Collisions MUST be prevented among values produced by different issuers. It could be a simple hash (making sure to include some fields which are unique globally, like a nonce), or it could be formatted as an URI).  

    The "jti" claim can be used to prevent the JWT from being replayed, as mentioned in section 4.1.7 of the [JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519#section-4.1.7) specification.

* **"cbu"**("Service Provider callback url"): [REQUIRED] this is the return url so that the wallet knows where to make the next call.

* **"iss"** (“issuer” in the VC spec): [REQUIRED] The value of this property is a DID representing the Alastria.ID of the entity that sent the Presentation Request. Dereferencing the DID results in a document containing machine-readable information about the requester that may be used to verify the information expressed in the Presentation Request.

* **"iat"** (Issued at): [REQUIRED] Identifies the time at which the JWT (that is, the Presentation Request) was issued. This field can be used to determine the age of the Presentation Request.  Its value MUST be a number containing a NumericDate value.

    A **NumericDate** value is a JSON numeric value representing the number of seconds from 1970-01-01T00:00:00Z UTC until the specified UTC date/time, ignoring leap seconds. This is equivalent to the IEEE Std 1003.1,  2013 Edition [POSIX.1] definition "Seconds Since the Epoch", in which each day is accounted for by exactly 86400 seconds, other than that non-integer values can be represented.  See RFC 3339 [RFC3339] for details regarding date/times in general and UTC in particular.

* **"exp"** (Expiration time): [OPTIONAL] The "exp" (expiration time) field identifies the expiration time on or after which the JWT (Presentation Request) MUST NOT be accepted for processing.  The processing of the "exp" field requires that the current date/time MUST be before the expiration date/time listed in the "exp" field.

    Implementers MAY provide for some small leeway, usually no more than a few minutes, to account for clock skew.  Its value MUST be a number containing a NumericDate value.

* "**procHash**" (Process Hash): [REQUIRED] The hash of an external document describing the intended purpose of the data that the service provider is requesting. This hash links the presentation to a specific Business Process Name & Description.

* "**procUrl**" (Process URL): [REQUIRED] The URL of an external document describing the intended purpose of the data that the service provider is receiving.

* **"data"**: [REQUIRED] It is the structure (JSON Array) that contains the actual Presentation Request data items. Each item in the array specifies a different field:
    *  **"@context"**: [REQUIRED] The context will be an array with https://alastria.github.io/identity/credentials/v1 and also the own of W3C https://www.w3.org/2018/credentials/v1. You can add more additional urls but these two will be compulsory.
    * "**type**": [REQUIRED] The type will be an array with "VerifiablePresentationRequest",  "AlastriaVerifiablePresentationRequest". More additional types can be added but these two will be mandatory.
    * **"levelOfAssurance"**: [OPTIONAL] Corresponds to the eIDAS assurance levels ("Self", “Low”, “Substantial”, “High”), plus an additional lower level “Self” for self-asserted data. It specifies the minimum LoA for the data field which is required by the entity sending the Presentation Request. If the field is not specified, the default is "Self".

    * **required**: [REQUIRED] Its value specifies if the field is compulsory (true) or optional (false).

    * **field_name**: [REQUIRED] The name of the required field, as defined in the ontology specified in **@context**.


## 5.3. Presentation Request Signature

The signature part is computed according to the JWS specification, without any modification or extension.

# 6. Private Metadata Sharing and Private Sharing Multi Hashes

[Credential & Presentations Life Cycle and PSM Hashes Technnical definition](https://github.com/alastria/alastria-identity/wiki/PSM-Hashes)
