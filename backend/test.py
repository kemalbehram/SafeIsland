# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This are the settings for the blockchain environment
# -------------------------------------------------------------------------

import os
from pathlib import Path

# For the data models
from pydantic import BaseSettings


# The settings set here can be overriden by ENVIRONMENT variables
class Settings(BaseSettings):

    # Set this to True to use production resources
    PERICO: str = "Inicial"

    class Config:
        secrets_dir = Path("private")

settings = Settings()

secretsPath = Path("private")
with open(secretsPath / "PERICO") as sec:
    secret = sec.readline()
    print(f"Secret: {secret}")

print(settings.PERICO)
