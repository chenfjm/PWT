# vim: set ts=4 et sw=4 sts=4 fileencoding=utf-8 :

from CCPRestSDK import REST
import logging

#主帐号
accountSid= 'aaf98f894bc4f9b9014bde7867430c1e'

#主帐号Token
accountToken= '63dc4df28b6b421f8073d6485885bd4d'

#应用Id
appId='8a48b5514bde8c71014be429b6af044a'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'

#模板ID
TMP_ID = 10000

log = logging.getLogger()

# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id

def sendTemplateSMS(to,datas,tempId):

    
    #初始化REST SDK
    rest = REST(serverIP,serverPort,softVersion)
    rest.setAccount(accountSid,accountToken)
    rest.setAppId(appId)
    
    result = rest.sendTemplateSMS(to,datas,tempId)
    for k,v in result.iteritems(): 
        
        if k=='templateSMS' :
                for k,s in v.iteritems(): 
                    log.info('%s:%s' % (k, s))
        else:
            log.info('%s:%s' % (k, v))
    
   
#sendTemplateSMS(手机号码,内容数据,模板Id)
if __name__ == '__main__':
    #sendTemplateSMS('18520222024', ['12','34'], TMP_ID)
