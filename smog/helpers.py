from hashlib import pbkdf2_hmac


def pw_hash(password, salt):
    return pbkdf2_hmac('sha512', password, salt, 100000)
