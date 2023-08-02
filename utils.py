import os
from passlib.context import CryptContext
from string import ascii_letters, ascii_lowercase, ascii_uppercase


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

def ceaser(text):
    result = ""
    for char in text:
        if char in ascii_letters:
            if char.isupper():
                shifted_char = ascii_uppercase[(ascii_uppercase.index(char) + 13) % 26]
            else:
                shifted_char = ascii_lowercase[(ascii_lowercase.index(char) + 13) % 26]
        else:
            shifted_char = str(char)
        result += shifted_char

    return result

