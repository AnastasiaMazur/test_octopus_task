import base64
import os
from Crypto import Random
from Crypto.PublicKey import RSA
from settings import PRIVATE_KEY_FILENAME


def generate_keys():
    if os.path.exists(PRIVATE_KEY_FILENAME):
        print("GET KEY FROM PATH")
        with open(PRIVATE_KEY_FILENAME, 'r') as f:
            PRIVATE_KEY = RSA.importKey(f.read())

    else:
        print("CREATE NEW KEY")
        random_generator = Random.new().read
        PRIVATE_KEY = RSA.generate(1024, random_generator)
        with open(PRIVATE_KEY_FILENAME, 'wb') as f:
            f.write(PRIVATE_KEY.exportKey('PEM'))

    PUBLIC_KEY = PRIVATE_KEY.publickey()
    print("CHECK KEYS IS FINISHED")
    return PRIVATE_KEY, PUBLIC_KEY


def encrypt_message(message_body, pub_key):
    encrypted_msg = pub_key.encrypt(message_body.encode(), 32)[0]
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)
    return encoded_encrypted_msg


def decrypt_message(encoded_message_body, priv_key):
    decoded_encrypted_msg = base64.b64decode(encoded_message_body)
    decoded_decrypted_msg = priv_key.decrypt(decoded_encrypted_msg)
    return decoded_decrypted_msg
