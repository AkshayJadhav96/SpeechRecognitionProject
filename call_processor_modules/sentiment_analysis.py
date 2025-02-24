"""Module: analyse_sentiment.

This module provides functionality to perform sentiment analysis on
transcribed text using the TextBlob library. The sentiment analysis calculates
the polarity and subjectivity of the text and classifies the overall sentiment
as Positive, Negative, or Neutral.

Features:
- Performs sentiment analysis on transcribed text.
- Returns polarity, subjectivity, and overall sentiment.
- Logs the sentiment results for analysis.
- Handles errors gracefully and provides default sentiment results.

Usage:
    ```python
    from analyse_sentiment import analyse_sentiment
    from call_processor_modules.pydantic_models import AnalyseSentimentInput

    input_data = AnalyseSentimentInput(transcribed_text="I am happy with the service.")
    output = analyse_sentiment(input_data)
    print(output)
    ```
"""


from textblob import TextBlob

from call_processor_modules.pydantic_models import (
    AnalyseSentimentInput,
    AnalyseSentimentOutput,
)
from logger_config import get_logger

logger = get_logger()

def analyse_sentiment(data: AnalyseSentimentInput) -> AnalyseSentimentOutput:
    """Perform sentiment analysis on transcribed text.

    :param data: AnalyseSentimentInput containing transcribed text.
    :return: AnalyseSentimentOutput with polarity and subjectivity scores.
    """
    try:
        text = data.transcribed_text
        logger.info("Starting sentiment analysis.")

        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        if polarity > 0:
            overall_sentiment = "Positive"
        elif polarity < 0:
            overall_sentiment = "Negative"
        elif polarity ==0:
            overall_sentiment = "Neutral"

        logger.info("Sentiment Analysis Results - Polarity: {polarity:.2f}, \
        Subjectivity: {subjectivity:.2f}, Overall Sentiment: {overall_sentiment}")

        return AnalyseSentimentOutput(
        polarity=polarity, subjectivity=subjectivity,
        overall_sentiment=overall_sentiment)

    except Exception:
        logger.exception("Error in sentiment analysis")
        return AnalyseSentimentOutput(
        polarity=0.0, subjectivity=0.0, overall_sentiment="Neutral")
