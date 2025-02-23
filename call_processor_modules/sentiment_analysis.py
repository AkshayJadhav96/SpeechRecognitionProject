from call_processor_modules.pydantic_models import AnalyseSentimentInput, AnalyseSentimentOutput
from textblob import TextBlob

from logger_config import get_logger

logger = get_logger()

def analyse_sentiment(data: AnalyseSentimentInput) -> AnalyseSentimentOutput:
    """
    Performs sentiment analysis on transcribed text.

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

        logger.info(f"Sentiment Analysis Results - Polarity: {polarity:.2f}, Subjectivity: {subjectivity:.2f}, Overall Sentiment: {overall_sentiment}")

        return AnalyseSentimentOutput(polarity=polarity, subjectivity=subjectivity, overall_sentiment=overall_sentiment)

    except Exception as e:
        logger.exception("Error in sentiment analysis")
        return AnalyseSentimentOutput(polarity=0.0, subjectivity=0.0, overall_sentiment="Neutral")
