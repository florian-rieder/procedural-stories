import os
import getpass

from langchain_ollama import ChatOllama
from langchain_fireworks import ChatFireworks
from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.globals import set_verbose
from langchain.globals import set_debug

from dotenv import load_dotenv

load_dotenv()

# These don't work well...
# set_debug(True)
# set_verbose(True)

# Use local model or cloud model ?
USE_LOCAL_MODEL = True
MAX_TOKENS = 2048

model = None
predictable_model = None

if USE_LOCAL_MODEL:
    print("Loading local model...")

    model = ChatOllama(
        model="llama3.1:8b",
        temperature=1.0,
        num_predict=2048,
        timeout=None,
        max_retries=0,
    )
    predictable_model = ChatOllama(
        model="llama3.1:8b",
        temperature=0.0,
        num_predict=1024,
        timeout=None,
        max_retries=0,
    )

    print("Local model loaded.")

else:
    # Use Fireworks
    if "FIREWORKS_API_KEY" not in os.environ:
        os.environ["FIREWORKS_API_KEY"] = getpass.getpass(
            "Enter your Fireworks API key: "
        )

    print("Loading Fireworks model...")
    model = ChatFireworks(
        # model="accounts/fireworks/models/llama-v3-70b-instruct",
        model="accounts/fireworks/models/llama-v3p1-8b-instruct",
        temperature=0.6,
        max_tokens=4096,
        timeout=None,
        max_retries=0,
        # other params...
    )

    predictable_model = ChatFireworks(
        model="accounts/fireworks/models/llama-v3p1-8b-instruct",
        temperature=0,
        max_tokens=1024,
        timeout=None,
        max_retries=0,
        # other params...
    )
    print("Fireworks model loaded.")
