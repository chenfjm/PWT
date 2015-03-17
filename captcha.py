# vim: set ts=4 et sw=4 sts=4 fileencoding=utf-8 :

import os
import base64  
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from random import randint
from cStringIO import StringIO

CHAR = 'acdefhjkmnprstuvwxyABCDEFHJKLMNPQRSTUVWXY345789'
LEN = len(CHAR) - 1
PADDING = 30 #图的边留白 
X_SPACE = 8 #两个字符之间的最少间隔
TRY_COUNT = 40 #随机出字符位置时最多尝试多少次
WIDTH = 60
HEIGHT = 40
FONT = ImageFont.load(os.path.join(os.path.dirname(__file__), 'font.pil'))

def gen():
    im = Image.new('1', (WIDTH, HEIGHT), 'white')
    draw = ImageDraw.Draw(im)
    w, h = im.size

    #S = [(x, y, 'c')]
    S = []
    x_list = []
    y_list = []
    n = 0
    while True:
        n += 1
        if n > TRY_COUNT:
            break
        x = randint(0, w - PADDING)
        flag = True
        for i in x_list:
            if abs(x - i) < X_SPACE:
                flag = False
                continue
            if not flag:
                break
        if not flag:
            continue

        y = randint(0, h - PADDING)
        x_list.append(x)
        y_list.append(y)
        S.append((x, y, CHAR[randint(0, LEN)]))
        if len(S) == 4:
            break

    for x, y, c in S:
        draw.text((x, y), c, font=FONT)

    #加3根干扰线
    for i in range(3):
        x1 = randint(0, (w - PADDING) / 2)
        y1 = randint(0, (h - PADDING / 2))
        x2 = randint(0, w)
        y2 = randint((h - PADDING / 2), h)
        draw.line(((x1, y1), (x2, y2)), fill=0, width=1)

    S.sort(lambda x, y: 1 if x[0] > y[0] else -1)
    char = [x[2] for x in S]
    output = StringIO()
    im.save(output, 'jpeg', quality=95)
    imgdata = output.getvalue()
    output.close()
    return ''.join(char), imgdata

if __name__ == '__main__':
    imgcode, imgdata = gen()
    print imgcode
    print base64.b64encode(imgdata)
