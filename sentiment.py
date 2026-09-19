from textblob import TextBlob


def analyze_sentiment(text):

    try:

        polarity = TextBlob(text).sentiment.polarity

        if polarity > 0.10:
            label = "Positive"

        elif polarity < -0.10:
            label = "Negative"

        else:
            label = "Neutral"

        return {
            "label": label,
            "score": round(polarity, 3)
        }

    except Exception:

        return {
            "label": "Neutral",
            "score": 0
        }