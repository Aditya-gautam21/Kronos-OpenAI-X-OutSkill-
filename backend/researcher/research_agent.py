import os
from contextlib import redirect_stderr
from backend.local_llm import get_llm
from backend.researcher.indicators import TechnicalIndicators
from backend.researcher.sentiment import SentimentAnalyzer
from backend.researcher.summary import summarize_for_llm
from backend.utils.prompts import Prompts
from backend.deepseek_llm import get_deepseek_llm

class ResearchAgent:
    def __init__(self):
        get_deepseek_llm()

    def research(self):
        technical_data = TechnicalIndicators().ohlcv_indicators_combined()
        sentiment_data = SentimentAnalyzer().fetch_and_analyze(hours=24)

        summary = summarize_for_llm(df=technical_data, sentiment_results=sentiment_data)

        prompt = Prompts.research_prompt(summary, technical_data)

        response = get_deepseek_llm().invoke([
                {
                    'role': 'system',
                    'content': prompt
                },
                {
                    'role': 'user',
                    'content': 'Analyze the market data above and output your trade plan.',
                }
            ],
            temperature=0.21
        )

        return response.content