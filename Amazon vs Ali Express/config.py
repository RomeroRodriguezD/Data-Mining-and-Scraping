import os
import binascii

def get_secret_key():
    secret_key = os.urandom(24)
    secret_key_hex = binascii.hexlify(secret_key).decode('utf-8')

    return secret_key_hex