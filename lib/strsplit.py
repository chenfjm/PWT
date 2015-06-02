# vim: set ts=4 et sw=4 sts=4 fileencoding=utf-8 :

import os
import sys

def strsplitnum(string, splitnum, splitstr='\n'):
    """按指定数组字数分割字符串
    """
    if not isinstance(splitnum, list):
        return string

    allnum = sum(splitnum)
    strlen = len(string)
    newlist = []
    start = 0
    if strlen <= allnum:
        for length in splitnum:
            newlist.append(string[start:start+length])
            start += length 
    else:
        a = (strlen - allnum) / splitnum[-1]
        b = (strlen - allnum) % splitnum[-1]
        newlen = a + (1 if b > 0 else 0)
        newsplitnum = splitnum + [splitnum[-1] for x in range(newlen)]
        for length in newsplitnum:
            newlist.append(string[start:start+length])
            start += length 
    return splitstr.join(newlist)

if __name__ == '__main__':

    str = u'我的分割字符串测试'
    new = strsplitnum(str, [2, 3, 2, 1])
    print new

