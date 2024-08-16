from random import randint
from string import ascii_letters, digits

CHARS = digits + ascii_letters


def randstr(length: int = 16, /) -> str:
    last_char = len(CHARS) - 1
    return ''.join(CHARS[randint(0, last_char)] for _ in range(length))
