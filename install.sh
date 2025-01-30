#!/bin/bash

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install Poetry
pip3 install poetry

# Install dependencies
poetry install --no-root