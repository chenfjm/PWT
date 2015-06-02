# vim: set ts=4 et sw=4 sts=4 fileencoding=utf-8 :

import os
import sys
HOME = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(HOME))
import time
import json
import hashlib
import logging
import tool
import datetime
import traceback
import urllib, urllib2, random

from pwt.web import template
from pwt.web import core
from pwt.base.qfresponse import *
from pwt.base.dbpool import with_database
from c.auth.bindwx import user_wxbind
from lib import coupon
import config

from .sdk import WxRequest,WxTextResponse,WxArticle,WxNewsResponse

log = logging.getLogger()

GUANZHU = u"""
欢迎关注
"""

class Weixin(core.Handler):
    def GET(self):
        """微信服务器验证接口
        """
        token = 'qianfang001'
        data = self.req.input()
        if not data:
            self.write('')
            return

        signature = data.get('signature', '') #data['signature']
        timestamp = data.get('timestamp', None)
        nonce     = data.get('nonce', None)
        echostr   = data.get('echostr', None)

        log.info("weixin certification interfac, esignature:%s timestamp:%s nonce:%s" % (signature, timestamp, nonce))
        a = [token, timestamp, nonce]
        a.sort()
        tmpstr = "%s%s%s" % tuple(a)
        hashstr = hashlib.sha1(tmpstr).hexdigest()
        if hashstr == signature:
            self.write(echostr)
        else:
            self.write('')
        return

    @with_database('qf_wemall')
    def POST(self):
        postdata = self.req.postdata()
        wxreq = WxRequest(postdata)

        merid = ''
        try:
            ret = self.db.select_one('merchant_wxconfig',
                    fields=('merid'),
                    where={'wxid': wxreq.ToUserName})
            if ret:
                merid = ret['merid']
        except:
            pass

        if wxreq.MsgType == 'event':
            if wxreq.Event == 'subscribe':
                try:
                    ret = self.db.select_one('merchant_wx_autoreply',
                            fields=('reply_id', 'reply_text', 'type'),
                            where={'merid': merid, 'action': 1})
                    if ret and ret['type'] == 0:
                        wxresp = WxTextResponse(ret['reply_text'], wxreq)
                        self.write(wxresp.as_xml())
                    elif ret and ret['type'] == 1:
                        pass
                    meruser, userid, mobile = user_wxbind(self.db, merid, wxreq.FromUserName)
                    coupon_id, coupon_nums = coupon.couponuser_rule(self.db, merid, 1, meruser=meruser, openid=wxreq.FromUserName)
                    if coupon_id and coupon_nums:
                        for l in range(coupon_nums):
                            coupon_sn, amount_sharekey, title = coupon.couponuser_new(self.db, coupon_id, meruser)
                        log.info('coupon_id=%s|meruser=%s' % (coupon_id, meruser))
                        try:
                            if coupon_sn and title:
                                if isinstance(amount_sharekey, long):
                                    message = u'优惠券来啦！恭喜您获得%s个面值%s元的%s' % (coupon_nums, float(amount) / 100.00, title)
                                else:
                                    message = u'优惠券来啦！恭喜您获得%s个%s, 点击以下链接地址领取: %s' % (coupon_nums, title, "http://%s/c/play/%s" % (self.req.host, amount_sharekey))
                                tool.weixin_send_msg(self.db, merid, wxreq.FromUserName, message.encode('utf-8'))
                        except:
                            pass
                    return
                except Exception:
                    log.warn(traceback.format_exc())

            elif wxreq.Event == 'CLICK':
                eventkey = wxreq.EventKey
                try:
                    ret = self.db.select_one('merchant_wxmenu',
                            fields=('menukey', 'name', 'action', 'keyword', 'skipurl'),
                            where={'merid': merid, 'menukey': eventkey})
                    if not ret:
                        wxresp = WxNewsResponse([], wxreq)
                        self.write(wxresp.as_xml())
                        return

                    if ret['action'] == 3:
                        wxresp = WxTextResponse(ret['keyword'], wxreq)
                    else:
                        ar = [WxArticle(
                                Title=ret['name'],
                                Description=ret['keyword'],
                                PicUrl=u'http://%s/static/imgs/default_mesg.png' % self.req.host,
                                Url=ret['skipurl'] + u'?openid=' + wxreq.FromUserName)]
                        wxresp = WxNewsResponse(ar, wxreq)
                    self.write(wxresp.as_xml())
                    return
                except:
                    pass
            else:
                wxresp = WxNewsResponse([], wxreq)
                self.write(wxresp.as_xml())
                return
        elif wxreq.MsgType == 'text':
            keyword = wxreq.Content
            ret = self.db.select_one('merchant_wx_autoreply', where={'merid': merid, 'keyword': keyword, 'action': 0})
            if ret:
                if ret['type'] == 0:
                    wxresp = WxTextResponse(ret['reply_text'], wxreq)
                    self.write(wxresp.as_xml())
                    return
                elif ret['type'] == 1:
                    pass

