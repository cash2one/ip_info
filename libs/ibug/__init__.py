#encoding=utf-8
'''
处理ibug相关接口
请求参数说明
user (required)
用户域账号名
eg:
user=chenxiang

pmt
PMT ID
eg:
pmt=4511

status
是否为未处理，是填1
eg:
status=1

env
Environment
环境，说明：1=>Production 2=>Dev 3=>Test 4=>Prerelease
eg:
env=1

URL举例说明
http://ibug.corp.anjuke.com/api/buglist?pmt=4511&user=chenxiang
'''
import json,urllib

class Ibug:
    def __init__(self,username='',pmt='',env=2,status=1):
        self.requestListUrl = 'http://ibug.corp.anjuke.com/api/buglist?'
        self.requestInfoUrl = 'http://ibug.corp.anjuke.com/api/buginfo?'
        self.user = username
        self.pmt = pmt
        self.env = env
        self.status = status
        args = {}
        if self.user != '':
            args['user'] = self.user
        if self.pmt != '':
            args['pmt'] = self.pmt
        if self.env  in [ 1,2,3,4 ]:
            args['env'] = self.env
        if self.status in [0,1]:
            args['status'] = self.status
        if len(args) > 0:
            self.requestListUrl += urllib.urlencode(args)
        self.requestRemoteData()
        return

    '''
    请求远端
    返回值为返回纪录条数
    '''
    def requestRemoteData(self):
        try:
            curlHandle = urllib.urlopen(self.requestListUrl)
            ibugList = json.loads(curlHandle.readline())

            if ibugList['status'] == 'ok' and ibugList['result']['count'] > 0:
                self.ibugList = ibugList['result']['data']
            else:
                self.ibugList = []
        except ValueError:
            self.ibugList = []

        return len(self.ibugList)

    '''
    获取ibug返回记录Id列表
    '''
    def getIdList(self):
        return self.ibugList

    '''
    通过id获取返回记录详细信息
    '''
    def getDetailInfoById(self,ibugIds):
        if len(ibugIds) > 0 :
            strIbugIdListResult = json.dumps(ibugIds)
            requestUrl = self.requestInfoUrl+"id="+strIbugIdListResult
            curlHandle = urllib.urlopen(requestUrl)
            result = json.loads(curlHandle.readline())
            if result['status'] == 'ok' and result['result']['count'] > 0:
                return result['result']['data']
        return []

    def getDetailInfos(self):
        return self.getDetailInfoById(self.ibugList)

if __name__ == 'main':
    pass
