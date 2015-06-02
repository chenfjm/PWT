#coding:utf-8

import hashlib
import random
import types
import struct
import simplejson as json

# 文件头标志位                  
EXT_FLAG = {
        'FFD8FF': 'EXT_JPG',
        '89504E47': 'EXT_PNG'       
    } 

def unicode2utf8(txt):
    if isinstance(txt, types.UnicodeType):
        return txt.encode('utf-8')
    else:
        return txt

def __hexdigest(algorithm, salt, raw_password):
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('"crypt" password algorithm not supported in this environment')
        return crypt.crypt(raw_password, salt)

    if algorithm == 'md5':
        return hashlib.md5(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")

def gen_password(raw_password):
    if raw_password is None:
        return '!'
    else:
        algo = 'sha1'
        salt = __hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = __hexdigest(algo, salt, raw_password)
        return '%s$%s$%s' % (algo, salt, hsh)

def check_password(raw_password, enc_password):
    algo, salt, hsh = enc_password.split('$')
    return hsh == __hexdigest(algo, salt, raw_password)

class ExtendedEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            if isinstance(o, datetime.date):
                return o.strftime(DATE_FORMAT)
            elif isinstance(o, datetime.datetime):
                return o.strftime(DATETIME_FORMAT)
            else:
                return JSONEncoder.default(self, o)
        except:
            return str(o)

# 字节码转16进制字符串
def bytes2hex(bytes):
    num = len(bytes)
    hexstr = ''

    for i in range(num):
        t = '%x' % bytes[i]
        if len(t) % 2:
            hexstr += '0'
        hexstr += t
    return hexstr.upper()


# 获取文件类型
def __streamtype(src):
    ftype = 'UNKNOWN'
    head = src[:14]
    for hcode in EXT_FLAG.keys():
        numOfBytes = len(hcode) / 2
        hbytes = struct.unpack_from('B' * numOfBytes, head[:numOfBytes])  # 'B'表示一个字节
        f_hcode = bytes2hex(hbytes)
        if f_hcode == hcode:
            ftype = EXT_FLAG[hcode]
            break

    return ftype

def streamtype(stream):
    return __streamtype(stream)
