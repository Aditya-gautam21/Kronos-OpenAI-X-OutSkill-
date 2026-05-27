import os
import logging
from dotenv import load_dotenv
from llama_cpp import Llama

load_dotenv()

logging.getLogger("llama_cpp").setLevel(logging.CRITICAL)

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = Llama(
            model_path=os.getenv("LOCAL_MODEL_PATH"),
            n_gpu_layers=24,
            n_ctx=3072,
            n_threads=4,
            use_mlock=True,
            verbose=False,
        )
    return _llm