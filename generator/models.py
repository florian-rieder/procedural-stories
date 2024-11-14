import os
import getpass

from langchain_community.llms.mlx_pipeline import MLXPipeline
from langchain_community.chat_models.mlx import ChatMLX
from langchain_fireworks import ChatFireworks
from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.globals import set_verbose
from langchain.globals import set_debug

from dotenv import load_dotenv

load_dotenv()

# These don't work well...
# set_debug(True)
set_verbose(True)

# Use local model or cloud model ?
USE_LOCAL_MODEL = False
MAX_TOKENS = 2048

model = None
predictable_model = None

print('Loading model...')
if USE_LOCAL_MODEL:
    # Load model from huggingface, using the MLX framework to take advantage of
    # Apple Silicon chips
    _llm = MLXPipeline.from_model_id(
        # 8bit quantization seems to be the sweet spot for speed and accuracy
        "mlx-community/Meta-Llama-3.1-8B-Instruct-8bit",

        # 16bit quantization or even full weight could give better results, but use more memory and
        # processing.
        # "mlx-community/Meta-Llama-3.1-8B-Instruct-bf16",
        # "mlx-community/Meta-Llama-3.1-8B-Instruct",

        # Let's try using a larger model, see if that improves results
        # "mlx-community/Qwen2.5-32B-Instruct-4bit",

        # Unfortunately, this is insufficient to handle nuance, although it is
        # surprisingly capable for such a small model.
        # "mlx-community/Llama-3.2-3B-Instruct-8bit",

        pipeline_kwargs={
            "max_tokens": MAX_TOKENS,
            "temp": 0.2,
            "repetition_penalty": 1.2
        },
    )

    # We load a second model with a temperature because we couldn't find how to
    # change that setting on the fly.
    # But in principle, changing the temperature of 0 on the same model is doable, so
    # this still counts as using one 8B model for the conversation loop and processing.
    _predictable_llm = MLXPipeline.from_model_id(
        "mlx-community/Meta-Llama-3.1-8B-Instruct-8bit",
        pipeline_kwargs={
            "max_tokens": MAX_TOKENS,
            "temp": 0,
            "repetition_penalty": 1.2
        },
    )

    model = ChatMLX(llm=_llm)
    predictable_model = ChatMLX(llm=_predictable_llm)

else:
    # Use Fireworks
    if "FIREWORKS_API_KEY" not in os.environ:
        os.environ["FIREWORKS_API_KEY"] = getpass.getpass("Enter your Fireworks API key: ")

    print('Loading Fireworks model...')
    model = ChatFireworks(
        model="accounts/fireworks/models/llama-v3-70b-instruct",
        temperature=0.6,
        max_tokens=4096,
        timeout=None,
        max_retries=0,
        # other params...
    )

    predictable_model = ChatFireworks(
        model="accounts/fireworks/models/llama-v3p1-8b-instruct",
        temperature=0,
        max_tokens=256,
        timeout=None,
        max_retries=0,
        # other params...
    )
    print('Fireworks model loaded.')
print('Model loaded.')
