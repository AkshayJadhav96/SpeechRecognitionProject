from call_processor_modules.pydantic_models import AnalyseSentimentInput, AnalyseSentimentOutput
from textblob import TextBlob

def analyse_sentiment(data: AnalyseSentimentInput) -> AnalyseSentimentOutput:
    text = data.transcribed_text
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    return AnalyseSentimentOutput(polarity=polarity, subjectivity=subjectivity)
