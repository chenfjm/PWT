# vim: set ts=4 et sw=4 sts=4 fileencoding=utf-8 :

import os
import sys
HOME = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(HOME))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(HOME)), 'conf'))
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

import constants

def aes_encode(text):
    mode = AES.MODE_CBC
    encryptor = AES.new(constants.ENCDEC_AES_KEY, mode, b'0100000000111000')
    length = 16
    count = len(text)
    if count < length:
        add = (length - count)
        #\0 backspace
        text = text + (' ' * add)
    elif count > length:
        add = (length - (count % length))
        text = text + ('\0' * add)
    return b2a_hex(encryptor.encrypt(text))

def aes_decode(text):
    mode = AES.MODE_CBC
    cryptor = AES.new(constants.ENCDEC_AES_KEY, mode, b'0100000000111000')
    plain_text = cryptor.decrypt(a2b_hex(text))
    return plain_text.rstrip('\0')

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print 'pyaes enc/dec key'
        os._exit(1)

    if sys.argv[1] == 'enc':
        print aes_encode(sys.argv[2])
    elif sys.argv[1] == 'dec':
        print aes_decode(sys.argv[2])
    else:
        print 'pyaes enc/dec key'
