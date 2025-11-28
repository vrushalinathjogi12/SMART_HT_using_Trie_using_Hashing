import re
def tokenize(text: str):
    if not text:
        return []
    return [t.lower() for t in re.findall(r'\b\w+\b', text)]
