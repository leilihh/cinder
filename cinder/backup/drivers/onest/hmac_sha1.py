# -*- coding: utf-8 -*-

import sha
import string
import base64


def xor_strings(s1, s2):
    """Pass two strings of the same length; returns their
    bit-wise exclusive or.
    """
    char_list = map(lambda x, y: chr(ord(x) ^ ord(y)), s1, s2)
    return string.join(char_list, "")


def hmac(message, key, hash_function, block_size):
    """Generic HMAC, as per RFC 2104.  The hash function must
    follow the usual Python new..update..digest interface.
    """
    if len(key) > block_size:
        key = hash_function.new(key).digest()
    ipad = chr(0x36) * block_size
    opad = chr(0x5C) * block_size
    key += chr(0) * (block_size - len(key))
    hash1 = hash_function.new(xor_strings(key, ipad))
    hash1.update(message)
    hash2 = hash_function.new(xor_strings(key, opad))
    hash2.update(hash1.digest())
    return hash2.digest()


def hmac_sha1(message, key):
    m = bytes(message.encode('utf-8'))
    k = bytes(key.encode('utf-8'))
    return base64.b64encode(hmac(m, k, sha, 64))
