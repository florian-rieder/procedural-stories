#!/bin/bash

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install Poetry
pip install poetry

# Install dependencies
poetry install --no-root