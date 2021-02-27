# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This are the settings for the blockchain environment
# -------------------------------------------------------------------------

import os
from pathlib import Path

# For the data models
from typing import Any, Dict, Tuple, Optional, cast
from pydantic import BaseModel, BaseSettings


# The settings set here can be overriden by ENVIRONMENT variables
class Settings(BaseSettings):

    # Set this to True to use production resources
    PRODUCTION: bool = False
    BLOCKCHAIN_NETWORK = "REDT"

    # Address of the blockchain node to use (development/production)
    BLOCKCHAIN_NODE_IP_PRODUCTION: str = "HTTP://15.236.0.91:22000"
    BLOCKCHAIN_NODE_IP_DEVELOPMENT: str = "HTTP://127.0.0.1:7545"
    BLOCKCHAIN_NODE_IP = BLOCKCHAIN_NODE_IP_DEVELOPMENT

    # The directory where the tool is invoked
    INITIAL_DIR: str = os.getcwd()

    # Directories with sources of the Smart Contracts and deployment artifacts
    CONTRACTS_DIR = os.path.join(INITIAL_DIR, "smartcontracts", "src")
    CONTRACTS_OUTPUT_DIR_DEVELOPMENT = os.path.join(INITIAL_DIR, "smartcontracts", "test_deploy")
    CONTRACTS_OUTPUT_DIR_PRODUCTION = os.path.join(INITIAL_DIR, "smartcontracts", "deploy")
    CONTRACTS_OUTPUT_DIR = CONTRACTS_OUTPUT_DIR_DEVELOPMENT

    # Location of Solidity compiler
    SOLC_DIR = os.path.join(INITIAL_DIR, "solc")

    # Location of EUTL input files (XML format)
    TRUSTED_LISTS_DIR = os.path.join(INITIAL_DIR, "eutl")

    # Location and name of the SQLite database with local config data
    DATABASE_DIR = os.path.join(INITIAL_DIR)
    DATABASE_NAME = os.path.join(DATABASE_DIR, "pubcred_config.sqlite")

    # Protect the server against clients sending big requests
    MAX_CONTENT_LENGTH: int = 30000

    # Configuration for the cache of the Secure Messaging Server
    TTLCACHE_NUM_ELEMENTS: int = 10000
    TTLCACHE_EXPIRATION: int = 60

    # Configuration of FastAPI API_KEY security system
    FASTAPI_SIMPLE_SECURITY_HIDE_DOCS = False
    FASTAPI_SIMPLE_SECURITY_DB_LOCATION = os.path.join(DATABASE_DIR, "apikeys.sqlite")
    FAST_API_SIMPLE_SECURITY_AUTOMATIC_EXPIRATION = 15
    FASTAPI_SIMPLE_SECURITY_SECRET = "dd4342a2-7d48-4d00-a118-21e63ac3449e"

    class Config:
        case_sensitive = True
        secrets_dir = "private"

settings = Settings()

# secretsPath = Path("private")
# with open(secretsPath / "PRODUCTION") as sec:
#     secret = sec.readline()
#     if secret.strip() == "True":
#         settings.PRODUCTION = True

if settings.PRODUCTION:
    settings.CONTRACTS_OUTPUT_DIR = settings.CONTRACTS_OUTPUT_DIR_PRODUCTION

if settings.BLOCKCHAIN_NETWORK == "REDT":
    settings.BLOCKCHAIN_NODE_IP = settings.BLOCKCHAIN_NODE_IP_PRODUCTION