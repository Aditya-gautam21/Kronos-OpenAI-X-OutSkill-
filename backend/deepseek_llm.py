import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

load_dotenv()

llm = ChatDeepSeek(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    model='deepseek-v4-flash'
    )
response = llm.invoke('what is the capital of India?')

print(response)