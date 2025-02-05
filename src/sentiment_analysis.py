from transformers import pipeline

# Initializing the sentiment analysis pipeline with a pre-trained model.
# The distilbert-base-uncased-finetuned-sst-2-english" model is well-suited for general sentiment tasks.
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(text):
    """
    Analyze the sentiment of the provided text

    Parameters: 
        text (str): The input text to analyze

    Returns:
        dict: A dictionary containing the sentiment label (e.g., 'POSITIVE', 'NEGATIVE')
            and the associated confidence score
    """

    # Checking if the text is empty or contains only whitespace.
    if not text.strip():
        # returning a default neutral sentiment if there's no content
        return {"label": "NEUTRAL", "score": 0.0}
    
    # Running the text through the sentiment pipeline
    result = sentiment_pipeline(text)[0]
    return result


if __name__ == '__main__':
    # Testing the sentiment analysis module with a sample text
    sample_text = "I absoluetly love this product! IT works like a charm."
    sentiment = analyze_sentiment(sample_text)
    print("Text:", sample_text)
    print("Sentiment:", sentiment)