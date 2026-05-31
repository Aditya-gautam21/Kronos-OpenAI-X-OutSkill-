import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from llama_cpp import Llama
from backend.deepseek_llm import get_deepseek_llm

load_dotenv(Path(__file__).resolve().parent / ".env")

logging.getLogger("llama_cpp").setLevel(logging.CRITICAL)

_llm = None
_use_deepseek = True  # flip to False to switch back to local model


def get_local_llm():
    """Original local llama-cpp model (kept as fallback)."""
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


def get_llm():
    if _use_deepseek:
        return get_deepseek_llm()
    return get_local_llm()