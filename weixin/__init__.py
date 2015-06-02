# vim: set ts=4 et sw=4 sts=4 fileencoding=utf-8 :

import weixin

URLS = (
    ('/api$', weixin.Weixin), #微信通知接口
)

