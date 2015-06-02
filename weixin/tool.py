# vim: set ts=4 et sw=4 sts=4 fileencoding=utf-8 :

import time
import json
import urllib
import urllib2

from redis.rediswrap import RedisCache


CACHE_TOKEN = 'weixin.access_token'
CACHE_APPID = 'weixin.appid'

WEIXIN_OAUTH_URL = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_base&state=1#wechat_redirect'

def get_access_token(merid, appid, secret):
    """获取全局TOKEN缓存
    """
    cache = RedisCache()

    token = ''
    value = None
    token_key = '%s.%s' % (CACHE_TOKEN, merid)
    try:
        value = cache.get(token_key)
        if value:
            token = value
    except:
        return token

    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (appid, secret)
    if not value:
        try:
            req = urllib2.Request(url)
            rsp = urllib2.urlopen(req)
            data = rsp.read()
            rsp.close()
            token = json.loads(data)['access_token']
            cache.set(token_key, token, 3600)
        except:
            return token
    return token

def weixin_gen_token(db, merid, appid, secret):
    """微信全局访问TOKEN创建
    """
    cache = RedisCache()

    value = None
    appid_key = '%s.%s' % (CACHE_APPID, merid)
    token_key = '%s.%s' % (CACHE_TOKEN, merid)
    try:
        value = cache.get(appid_key)
        if value:
            value = json.loads(value)
    except:
        return False

    if not value or value['appid'] != appid or value['secret'] != secret:
        data = {
            'appid': appid,
            'secret': secret,
        }
        cache.set(appid_key, json.dumps(data), 0)
        cache.delete(token_key)

    token = get_access_token(merid, appid, secret)
    if not token:
        return False

    return True

def weixin_get_openid(db, merid, code):
    """获取用户的OPENID
    """
    cache = RedisCache()

    value = None
    appid_key = '%s.%s' % (CACHE_APPID, merid)
    try:
        value = cache.get(appid_key)
        if value:
            value = json.loads(value)
    except:
        return None

    if not value:
        try:
            ret = db.select_one('merchant_wxconfig', fields=('name', 'appid', 'appsecret'),
                    where={'merid': merid, 'is_deleted': 0})
            if not ret:
                return None
            appid  = ret['appid']
            secret = ret['secret']
        except:
            return None
    else:
        appid  = value['appid']
        secret = value['secret']

    token = get_access_token(merid, appid, secret)
    if not token:
        return None

    url = 'https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code' % (appid, secret, code)
    try:
        req = urllib2.Request(url)
        rsp = urllib2.urlopen(req)
        data = rsp.read()
        rsp.close()
    except:
        return None

    return json.loads(data)

def weixin_send_msg(db, merid, openid, msg):
    """微信单条发送消息
    """
    cache = RedisCache()

    value = None
    appid_key = '%s.%s' % (CACHE_APPID, merid)
    try:
        value = cache.get(appid_key)
        if value:
            value = json.loads(value)
    except:
        return None

    if not value:
        try:
            ret = db.select_one('merchant_wxconfig', fields=('name', 'appid', 'appsecret'),
                    where={'merid': merid, 'is_deleted': 0})
            if not ret:
                return None
            appid  = ret['appid']
            secret = ret['secret']
        except:
            return None
    else:
        appid  = value['appid']
        secret = value['secret']

    token = get_access_token(merid, appid, secret)
    if not token:
        return None

    data = None
    params = {'access_token': urllib.quote(token)}
    url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?%s' % urllib.urlencode(params)
    try:
        if isinstance(openid, unicode):
            openid = openid.encode('utf-8', 'ignore')
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8', 'ignore')
        req = urllib2.Request(url, '''{"touser":"%s","msgtype":"text","text":{"content":"%s"}}''' % (openid, msg))
        rsp = urllib2.urlopen(req)
        data = rsp.read()
        rsp.close()
    except:
        return None

    return data

def weixin_send_allmsg(db, merid, userlist, msg):
    """微信群发一个公众号消息
    """
    for u in userlist:
        send_weixin_msg(u, msg)

def weixin_get_userinfo(db, merid, openid):
    """微信获取用户信息
    """
    cache = RedisCache()

    value = None
    appid_key = '%s.%s' % (CACHE_APPID, merid)
    try:
        value = cache.get(appid_key)
        if value:
            value = json.loads(value)
    except:
        return None

    if not value:
        try:
            ret = db.select_one('merchant_wxconfig', fields=('name', 'appid', 'appsecret'),
                    where={'merid': merid, 'is_deleted': 0})
            if not ret:
                return None
            appid  = ret['appid']
            secret = ret['secret']
        except:
            return None
    else:
        appid  = value['appid']
        secret = value['secret']

    token = get_access_token(merid, appid, secret)
    if not token:
        return None

    data = None
    url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s' % (token, openid)
    try:
        req = urllib2.Request(url)
        rsp = urllib2.urlopen(req)
        data = rsp.read()
        rsp.close()
    except:
        return None

    return data

def weixin_make_mainmenu(db, merid, mainmenu):
    """微信创建菜单
    """
    cache = RedisCache()

    value = None
    appid_key = '%s.%s' % (CACHE_APPID, merid)
    try:
        value = cache.get(appid_key)
        if value:
            value = json.loads(value)
    except:
        return False

    if not value:
        try:
            ret = db.select_one('merchant_wxconfig', fields=('name', 'appid', 'appsecret'),
                    where={'merid': merid, 'is_deleted': 0})
            if not ret:
                return False
            appid  = ret['appid']
            secret = ret['secret']
        except:
            return False
    else:
        appid  = value['appid']
        secret = value['secret']

    token = get_access_token(merid, appid, secret)
    if not token:
        return False

    # 调整微信绑定菜单
#   for mm in mainmenu['button']:
#       if 'subbutton' in mm:
#           for m in mm['subbutton']:
#               if m['type'] == 'view':
#                   m['url'] = (WEIXIN_OAUTH_URL % (appid, urllib.quote(m['url']))).encode('utf-8', 'ignore')
#       elif mm['type'] == 'view':
#           mm['url'] = (WEIXIN_OAUTH_URL % (appid, urllib.quote(mm['url']))).encode('utf-8', 'ignore')

    params = {'access_token': urllib.quote(token)}
    data = {'errcode': 1, 'errmsg': '微信错误'}
    url = 'https://api.weixin.qq.com/cgi-bin/menu/create?%s' % urllib.urlencode(params)
    try:
        req = urllib2.Request(url, json.dumps(mainmenu, ensure_ascii=False))
        rsp = urllib2.urlopen(req)
        data = rsp.read()
        rsp.close()
    except Exception, e:
        return data

    data = json.loads(data)
    return data
