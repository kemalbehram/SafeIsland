# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This are the settings for the blockchain environment
# -------------------------------------------------------------------------

import os

# For the data models
from typing import Any, Dict, Tuple, Optional, cast
from pydantic import BaseModel, BaseSettings


# The settings set here can be overriden by ENVIRONMENT variables
class Settings(BaseSettings):

    PRODUCTION: bool = False

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

    class Config:
        secrets_dir = "private"

settings = Settings()

if settings.PRODUCTION:
    settings.BLOCKCHAIN_NODE_IP = settings.BLOCKCHAIN_NODE_IP_PRODUCTION
    settings.CONTRACTS_OUTPUT_DIR = settings.CONTRACTS_OUTPUT_DIR_PRODUCTION
    
