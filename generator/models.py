import os

from dotenv import load_dotenv

from tracet import ChatFireworks, ChatOllama, BaseLLM

load_dotenv()

# These don't work well...
# set_debug(True)
# set_verbose(True)

# Use local model or cloud model ?
USE_LOCAL_MODEL = True
MAX_TOKENS = 8192

model: BaseLLM = None


if USE_LOCAL_MODEL:
    print("Loading local model...")

    model = ChatOllama(
        model="llama3.1:8b",
        temperature=1.0,
        max_tokens=MAX_TOKENS,
    )

    print("Local model loaded.")
else:
    api_key = os.getenv("FIREWORKS_API_KEY")
    # Use Fireworks
    if api_key is None:
        raise ValueError("FIREWORKS_API_KEY not found in environment variables")

    print("Loading Fireworks model...")
    model = ChatFireworks(
        model="accounts/fireworks/models/llama-v3-70b-instruct",
        # model="accounts/fireworks/models/llama-v3p1-8b-instruct",
        api_key=api_key,
        temperature=1.0,
        max_tokens=MAX_TOKENS,
    )
    print("Fireworks model loaded.")
