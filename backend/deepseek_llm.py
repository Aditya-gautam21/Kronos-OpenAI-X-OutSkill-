import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv(Path(__file__).resolve().parent / ".env")

_deepseek_llm = None


class DeepSeekLLM:

    def __init__(self, chat: ChatDeepSeek):
        self._chat = chat

    def create_chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.25,
        **kwargs,
    ) -> dict:
        self._chat.temperature = temperature

        langchain_messages = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:
                langchain_messages.append(HumanMessage(content=content))

        response = self._chat.invoke(langchain_messages)

        return {
            "choices": [
                {
                    "message": {
                        "content": response.content,
                        "role": "assistant",
                    }
                }
            ]
        }


def get_deepseek_llm():
    """Singleton DeepSeekLLM instance."""
    global _deepseek_llm
    if _deepseek_llm is None:
        llm = ChatDeepSeek(
            model="deepseek-chat",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            temperature=0.21,
            verbose=False,
            timeout=None,
            max_retries=2
        )
    return llm
