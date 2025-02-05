import re

def clean(text):
    """
    Cleans text by removing URLs, non-alphanumeric characters (except spaces), and extra spaces
    Parameters:
        text (str): The raw text string to clean.

    Returns:
        str: Cleaned text.
    """

    # Removing URLs
    text = re.sub(r'http\S+|wwwS+|https\S+', '', text, flags=re.MULTILINE)
    # Removing non-alphanumeric characters (excluding spaces)
    text =re.sub(r'[^A-Za-z0-9\s]+', '', text)
    # Removing extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

if __name__ == '__main__':
    # Testing the cleaning function with sample text
    sample_text = "Check out this link: https://example.com! Isn't it cool? #new"
    print("Original:", sample_text)
    print("Cleaned:", clean(sample_text))