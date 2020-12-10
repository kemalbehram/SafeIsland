# Public Credentials in blockchain

## User Journeys

### Main User Journey: finding and validating promotions

#### Uses mobile to enter the web-site of the promotions of Metrovacesa

There is a mobile web-app (non-native) that can be hosted and served and customized by anybody. That is, the mobile web-app can be deployed by anybody.

The app uses the smart contract AlastriaResolver to resolve the hierarchical name "metrovacesa.deconfianza.alastria" to get the CID (Content ID, which is an IPFS multihash) of the root of the credentials for Metrovacesa. The AlastriaResolver contract is deployed in Red T and its address is a well-known one and is published prominently in all possible sites. This is the only hardcoded address that should be used in the system.

The system allows to have the AlastriaResolver smart contract deployed in parallel in more than one blockchain network (eg. in LaCChain), with the only requirement being that the nodes of the Trust Framework are managed by the same entities or equivalent ones from the point of view of level of trust.

The app can use any blockchain node to access the Red T, but in any case the trust.evidenceledger.org gateway is publicly available for free implementing the APIs required in this system.

Once the app has the CID of the root of the credentials it uses any IPFS Gateway (public or private) to retrieve the list of credentials associated to the Metrovacesa credential root. For example, if the root CID from AlastriaResolver is `Qme3LTcP91hRWcjaPPTfikhKmfPCzENeGxt9C8iaXm4shB` and the app uses the public IPFS gateway `trust.evidenceledger.org`, the call would be `https://trust.evidenceledger.org/ipfs/Qme3LTcP91hRWcjaPPTfikhKmfPCzENeGxt9C8iaXm4shB`. The call returns a block of data with a format like this:

```
Qmeqaa16ZpXh5Y3g7jMQxnMJW6uj492hsEzvrvEvFW9S99 1128  altoariza.json
QmVvB5Jj2QH3WAcXYAVeRpHQXVKdG6ASXjZepp4sqanyz2 61364 altoariza.png
QmXAP59FptSd8z7ij5AGMswKNLXckUCNke5mMdkEP5SGbL 1185  jardinsdellevant.json
QmcwF4BpuUZDVfuqvk1TxGfYrtdYT2w4nxBoZswDgNigXN 66678 jardinsdellevant.png
QmeyAZQG8yNoECSLmkd41qo9CCBRARZBs1BCPkfLkVcJSF 1190  lasterrazasdeponientesur.json
QmcvH2atdR6Gs5WxBLued1Exri4TLkdPCGyo9sJXvJ2S41 66971 lasterrazasdeponientesur.png
QmVTUbEkC4WXxwgaQKVv3eovBu5nYNJJmZbVzMTZgZNsU3 1171  miradordelaalbaida.json
QmNUTx8iNDgTx3zPyw8x5jtxttBkVr9dHZNQe3q7ss2y9J 65806 miradordelaalbaida.png
QmWZ17hG726dUoSbYTbrUhRibatwZB69HUrFmWqx17YaCK 1131  nereidas.json
QmTqCkHWsZeXVQBVd2mKX7mm4M9ShCWYsezEeRNnF3wb6A 62021 nereidas.png
QmQxUvNJ9e8zGNqbJkrS6N7s1jhy6CFYNuecfUjsR85Do6 1182  porticodesimonverde.json
QmZgCrPjiFjaumBAoiiJWoWb1hrKY2KtGbV2JDZbAKR6gE 66154 porticodesimonverde.png
QmYVxGqmebMiKZYvVNjLstZoziEpJUbVUKhtwE67ypSmvM 1137  residencialamura.json
QmNqadcYnPRsLz3EuEuth1ypzkNEaFMGJ4qGUWNrugRnNS 66210 residencialamura.png
QmPGePod1Q1Bz8KMPBYCty77YhB84gnSyfY1eQKA8vx4Wi 1184  residencialatlantia.json
Qmc1uFsGCo2hwW9pGi9MeZHuZpLySkq5PGXfA2LyNV2CcR 67212 residencialatlantia.png
QmeYRao1RiYW8keHorZzZ8p3P1Ptd7D5jAeaJ4qpyvnb84 1164  residencialcitrea.json
QmUMTsm5g78f9vs2WZvXMf5a4aFwztKUa8tswR5LrGzJNC 64129 residencialcitrea.png
QmeAzXjuwrTrQBn3GVbjyTQicvnss5aGRdUbrKGqzPmqd7 1140  residencialhalia.json
QmeDmMLQf1cqHbRZxczkrtz49Pty9v5W5DsvSh34SapTry 66716 residencialhalia.png
QmeRWcuzZWCfNGBWQHrUVeQbHChQ7kbsUR7p4JUkfPxEB5 1166  residencialhesperides.json
QmYeSXKX3stNscrcTK25TTidWSiLRfx4FpQC4id4P65uNP 65156 residencialhesperides.png
QmY9o5nK5brLC3CnWB8qTR6rrLA1mxV8XMZJHatogJWZtq 1148  residencialimspirafasei.json
QmUBi1SJGg5LviRHBfvPRPQ5KzuQ7DEERbYdJjpm5wnDEu 66139 residencialimspirafasei.png
QmdsZmmkLe6FaHVgqzECqxJad4B9daWJ36YZbGMFKuLpRf 1163  residencialnovolerez.json
QmYPp9q4EGfHHrppejriJb4VDtzkagMcAYiHA8qyxoGHMy 67009 residencialnovolerez.png
QmSAQmio3DYeQQh5JRAeETkdxLnBjBDGDT7yjenvX6BBjP 1162  residencialq.json
QmbrDLjZUTuKGteKYMbzVRDKcdy17XqKpRPY8fgRw12dmg 65749 residencialq.png
QmcJ2tzbFT9ULVJfHuji8NetGqwZDM5Fkg1dKYRidRLWcF 1204  residencialtamadabai.json
QmZUdgLwVnm5Q136H8Go6yar1jXHHNsbwrWgxP9mKSQwaD 67836 residencialtamadabai.png
QmX8WNsXDE1y69ix5Q8ApM7SecJcDg6SZtxxpWjs8hp6Wd 1169  residencialtorredelsvents.json
QmVdwbzcmet3iVH1DzQm9QRbneUpUstHLfcH8dcBSe83TG 65634 residencialtorredelsvents.png
QmcTHTvf7jY5SXEHDVUJFMYwLM2ep1z6byGn87aBtRqSAV 1184  residencialxardinsdagaiteira.json
QmZQzPZ7cu4k584yqpd2ugykSPKtpWLJdyyPLbrmDS94RK 64426 residencialxardinsdagaiteira.png
QmPjxtAcuTjtHUKPVt8yCN1MKbtF9pevorud9FQeM9mVti 1170  villasdelavega.json
QmYSEKxbBHxxtVfNCkYMxb8fmpH5vA2w6vu3EPxxwuupLo 65202 villasdelavega.png
```

Each line represents a credential, and there are three fields. The first one is the CID of the credential, the second is the size of the file and the third one is the file name in the MFS (Mutable File System).

The CID of the credential can be used to recover details about it: the bulk of the data is stored in IPFS, while some metadata is stored in the blockchain (Red T). Both sets of data items are stored associted to the CID.

The app can use any IPFS Gateway to get the credential data in the form of a Verifiable Credential Image. The Verifiable Credential Image is a PNG image file with an embedded associated W3C Verifiable Credential inside the image data (in JSON format).

The Verifiable Credential Image can be obtained in two ways (as usual for files stored in IPFS). One is using its CID directly, and the other using the root CID plus the name of the credential image. For example:

```
https://trust.evidenceledger.org/ipfs/QmVvB5Jj2QH3WAcXYAVeRpHQXVKdG6ASXjZepp4sqanyz2

https://trust.evidenceledger.org/ipfs/QmXPvYMGSvGWEXXH5ftUW6rNid54d79MFVRKJS45oRkUrR/altoariza.png

```

To get the metadata of the Verifiable Credential Image from the blockchain, the app calls the AlastriaResolver smart contract with the CID of the credential. The data obtained is the following:

```
TODO: add the data
```

## Trust framework

Uses the same schema and similar concepts to the decentralized governance of the Internet, por example the DNS system. It is based in a combination of blockchain and IPFS: IPFS to hold the bulk of the data, and the hashes of the data will be anchored into the blockchain.

The system is hierarchical but at the same time can achieve high degrees of decentralization.

The trust at different levels is managed by several blockchain contracts, based on the ENS system of Ethereum, implemented in the Red T blockchain network.

### The Root of the system

At the root of everything is a **root of trust**. At the beginning (the genesis of the framework), the root is managed by a single entity which is the deployer of the ENS contract. This is called the "root record" in ENS.

So the system starts centralized, but when the ecosystem thinks it is appropriate, ownership of the root can be transferred to a smart contract that implements the appropriate governance model on behalf of the whole community around the Trust Framework.

Another option for improving decentralization when the system matures is that the ownership can be "cancelled", which means that nobody (even the deployer) will ever able to take control of the root, and the system will be completely autonomous since then. This would be the very good from the ideological standpoint, however the practical implications have to be analyzed carefully. For example, there can not be maintenance and upgrade operations of anything that needs root privileges.

Depending directly from the **root** there is a first layer of *top level trust nodes* (**TLTN**), to manage different aspects of the framework. The TLTNs can only be created by the owner of the Root node.

The owners of the TLTNs can be related among themselves, or could be completely independent. Once created, each TLTN can be managed independently of the root node and by a different entity (or set of entities). However, the owner of the root node has always the possibility of taking back control of the TLTNs. This is the reason for the importance of defining and implementing a proper governance model for the root node, or even for cancelling ownership of it completely at a given point in time.

The system is bootstrapped with several TLTNs, managing different aspects of the Trust Framework. The following is an example of a possible tree of trust.

```
ROOT
  |-- trust
  |     |-- ES Trusted List
  |     |-- FR Trusted List
  |     |-- DE Trusted List
  |     |-- ...
  |
  |-- pubcreds
  |     |-- deconfianza
  |     |      |-- metrovacesa
  |     |      |-- valladolid
  |     |      |-- cordoba
  |     |      |- "other deconfianza top-level entities"
  |     |
  |     |-- icte
  |     |-- responsibletourism
  |
  |-- ala
  |     |-- in2
  |     |-- bancosantander
  |     |-- bolsasymercados
  |     |-- "any standard DNS domain of the members of Alastria"
```

The different elements of the tree are explained in the following sections.  

### The List of Trusted Lists (LOTL)

One of the TLTNs (and a very special one) provides a function similar to the [European List of Trusted Lists (LOTL)](https://webgate.ec.europa.eu/tl-browser/#/). In ENS, its name is **"trust"**, which complies with the [UTS-46 normalization](https://unicode.org/reports/tr46/) required for domain names in ENS.

The hierarchy for this branch is the following:

```
ROOT
  |-- trust
  |     |-- ES Trusted List
  |     |-- FR Trusted List
  |     |-- DE Trusted List
  |     |-- ...
  |
```

The owner of the "trust" node can manage a list of other second-level nodes. Each second-level node is managed by a different entity, and each node is in reality another list of trusted nodes, in a similar way to how the TSLs are managed in eIDAS. Each of those nodes can be managed by a different entity.

The system is bootstrapped with the ES Trusted List, which is a *copy* of the official [Spanish Trusted List](https://sede.minetur.gob.es/prestadores/tsl/tsl.xml).


### The "pubcreds" TLTN and the "deconfianza" identities

The hierarchy is the following (including the "trust" branch described previously):

```
ROOT
  |-- trust
  |     |-- ES Trusted List
  |     |-- FR Trusted List
  |     |-- DE Trusted List
  |     |-- ...
  |
  |-- pubcreds
  |     |-- deconfianza
  |     |      |-- metrovacesa
  |     |      |-- valladolid
  |     |      |-- cordoba
  |     |      |- "other deconfianza top-level entities"
  |     |
  |     |-- icte
  |     |-- responsibletourism
  |
```

The node "pubcreds" helps manage the whole ecosystem of Public Verifiable Credentials. For the nodes depending from "pubcreds", the basic difference is the mechanism used for onboarding and verification of the real identities of the participants.

This is the reason for the three nodes in the example: "deconfianza", "icte" and "responsibletourism". The participants in the "pubcreds" ecosystem all manage Public Verifiable Credentials, but the identities of the issuers are verified in different ways, so the trust on the credentials issued by each participant may be different.

### The entities in the system

#### DECONFIANZA ecosystem

DECONFIANZA is a project in the Alastria ecosystem. It is not a legal entity (eg. registered in the Business Registry of Spain), but it provides an ecosystem for the participation of all other entities like local, regional or central public administrations, or private companies that register public credentials.

Even though DECONFIANZA is not incorporated as a legal entity it should exist as an entity in the trust framework because all participants collaborate in the definition and enforcement of the rules and procedures to enable the trust in the system.

In the Trust Framework the DECONFIANZA system is at:

```
ROOT -> pubcreds -> deconfianza
```

All credentials issued in the DECONFIANZA ecosystem will depend from some sub-node of the "deconfianza" node.
The "deconfianza" node is owned by the project governance committee, which is responsible for the rules to create sub-nodes.

#### Public credentials in DECONFIANZA

The DECONFIANZA credentials are issued and managed by some entity that participates in the ecosystem. Each credential is strongly related to the entity that issues the credential.

Each entity that issues credentials in the DECONFIANZA ecosystem should be represented as a sub-node of the "deconfianza" node. For example:

```
ROOT
  |-- pubcreds
  |     |-- deconfianza
  |     |      |-- metrovacesa
  |     |      |-- ferrovial
  |     |      |-- valladolid
  |     |      |-- cordoba
  |     |      |- "other deconfianza top-level entities"
  |     |
```

Please note that the *metrovacesa* and *ferrovial* nodes do not represent the identities of those companies, but instead they are the root nodes of the credentials issued by those companies. The identities of the companies exist in a different area of the Trust Framework.

Using the example of Metrovacesa, in the simplest case the *metrovacesa* node can be used as the root of all credentials issued by Metrovacesa. In more complex situations, the *metrovacesa* node can be managed autonomously by Metrovacesa which can create subnodes and manage them as it wishes. Metrovacesa can create subnodes to better structure and manage the different types of credentials. For the moment, we will assume here the simple case.

#### The local government

The credentials issued by local governments (eg. Valladolid) are also represented in the Trust Framework as a node. Using the example of Valladolid, it could be like this:

```
ROOT
+-- alastria
    +-- deconfianza
        +-- metrovacesa
        +-- valladolid
```

#### Other credential ecosystems (eg. ICTE, Responsible Tourism)

There may be other types of credentials issued and managed in the Alastria ecosystem. Two examples are ICTE and Responsible Tourism (Ministry of Tourism). They can be represented in the Trust Framework with corresponding nodes, like this:

```
ROOT
+-- alastria
    +-- deconfianza
        +-- metrovacesa
        +-- valladolid
    +-- icte
    +-- responsibletourism
```


```

```