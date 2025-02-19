from textblob import TextBlob

def analyse_sentiment(text):
    """
    Perform sentiment analysis on the transcribed text.
    Returns polarity and subjectivity scores.
    """
    # Analyze sentiment using TextBlob
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # Range: [-1, 1], where -1 is negative, 1 is positive
    subjectivity = blob.sentiment.subjectivity  # Range: [0, 1], where 0 is objective, 1 is subjective

    # Print results
    # print("\nSentiment Analysis Results:")
    # print(f"- Polarity: {polarity:.2f} (Negative to Positive)")
    # print(f"- Subjectivity: {subjectivity:.2f} (Objective to Subjective)")

    # Interpret polarity
    # if polarity > 0:
    #     print("  Overall Sentiment: Positive")
    # elif polarity < 0:
    #     print("  Overall Sentiment: Negative")
    # else:
    #     print("  Overall Sentiment: Neutral")

    return polarity, subjectivity