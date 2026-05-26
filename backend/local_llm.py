import os
from dotenv import load_dotenv
from llama_cpp import Llama

load_dotenv()

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = Llama(
            model_path=os.getenv("LOCAL_MODEL_PATH"),
            n_gpu_layers=21,
            n_ctx=2048,
            n_threads=4,
            use_mlock=True,
        )
    return _llm