from string import punctuation


def sanitize(value: str, /) -> str:
    value = ''.join(c for c in value.lower() if c not in punctuation)
    return ' '.join(word for word in value.split() if word)
