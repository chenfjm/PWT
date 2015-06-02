# vim: set ts=4 et sw=4 sts=4 fileencoding=utf-8 :

import os
import sys
import redis


REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

SYSTEM = {
    'default': redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
}


def get_redis(system='default'):
    return SYSTEM[system]

class RedisCounter(object):
    """Redis计数器
    """
    def __init__(self, system='default'):
        self.system = system

    def set(self, key, timeout=0):
        try:
            r = get_redis(self.system)
            c = r.incr(key)
            if timeout:
                r.expire(key, timeout)
        except Exception, e:
            return None
        return c

class RedisCache(object):
    """Redis缓存对象
    """
    def __init__(self, system='default'):
        self.system = system

    def set(self, key, value, timeout=0):
        try:
            if timeout:
                ret = get_redis(self.system).setex(key, value, timeout)
            else:
                ret = get_redis(self.system).set(key, value)
        except Exception, e:
            return False
        return ret

    def get(self, key):
        try:
            value = get_redis(self.system).get(key)
        except Exception, e:
            return None
        return value

    def delete(self, key):
        try:
            ret = get_redis(self.system).delete(key)
        except Exception, e:
            ret = 0
        return ret

if __name__ == '__main__':

    rds = RedisCache()
    print rds.set('20140530174900', '{"a":1,"b":2}', 0)
    print rds.get('20140530174900')
    print rds.delete('20140530174900')
    print rds.get('20140530174900')
    
    rds = RedisCounter()
    print rds.set('19000000', 1)

