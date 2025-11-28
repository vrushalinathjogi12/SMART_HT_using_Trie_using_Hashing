import re

def preprocess_text(text: str) -> str:
    """
    Clean and normalize text before indexing/searching.
    Includes:
    - lowercasing
    - removing special characters
    - keeping alphanumeric and spaces
    - reducing repeated spaces
    """
    if not text:
        return ""

    # lowercase
    text = text.lower()

    # remove unwanted chars
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text
