# coding: utf-8

import logging
import datetime
import random
import time
import re
import redis
import base64
import uuid
from captcha import captcha

log = logging.getLogger()
redis_data = redis.Redis(host='127.0.0.1', port="6379", db=1)


def check_verifycode()
    try:
        form = self.req.inputjson()
        code_id = form.get('uuid').strip()
        code_value = form.get('capchacode').strip()
        code = redis_data.get(code_id)
        if code_value.lower() != code.lower():
            self.write(error(QFRET.REQERR, data="验证码错误", escape=False))
            return


def generate_verifycode():
    code, img_string = captcha.gen()
    base64_img = base64.b64encode(img_string)
    code_id = str(uuid.uuid1())
    try:
        redis_data.setex(code_id, code, config.redisConfig["time"])
    except:
        log.error(traceback.format_exc())
        return False

    base64_img = "data:image/jpg;base64,%s" % base64_img
    member_info = {'uuid': code_id, 'img': base64_img}

    return member_info

class Verifycode(core.Handler):
    def POST(self):
        start_time = time.time()
        self.set_headers({'Content-Type': 'application/json; charset=UTF-8'})

        verify_data = generate_verifycode()

        if not verify_data:
            log.info('respcd=%s|path=%s|time=%sms' % (QFRET.THIRDERR, self.req.path, (time.time() - start_time) * 1000))
            self.write(error(QFRET.THIRDERR, escape=False).encode('utf-8'))
            return

        log.info('respcd=%s|path=%s|time=%sms' % (QFRET.OK, self.req.path, (time.time() - start_time) * 1000))
        self.write(success(data=verify_data, escape=False).encode('utf-8'))
        return
