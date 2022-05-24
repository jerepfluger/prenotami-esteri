from os import environ as env

from cryptography.fernet import Fernet


class Cipher(object):
    def __init__(self):
        self.cipher = Fernet(env['CIPHER_KEY'])

    def encrypt(self, data):
        return self.cipher.encrypt(data.encode('utf-8'))

    def decrypt(self, data):
        return self.cipher.decrypt(data.encode('utf-8')).decode('utf-8')
