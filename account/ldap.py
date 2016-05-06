#------------------------------------OAUTH--------------------------------------------#
#------------------------------------OAUTH--------------------------------------------#
#------------------------------------OAUTH--------------------------------------------#

from urllib import urlencode
from urllib2 import urlopen
from json import loads as json_decode
from urllib2 import Request

def authenticate(username, password, api_url, getinfo=False):
    if username and password and api_url:
        param = {}
        param['u'] = username
        param['p'] = password
        if getinfo:
            param['f'] = 'getinfo'

        req = Request(api_url, urlencode(param))

        raw_info = urlopen(req).read()
        info = json_decode(raw_info)

        if not getinfo and info['status']:
            return True

        user = {}
        if check_reslut(info):
            user['id'] = info['result'][0]['english_name']
            user['name'] = info['result'][0]['chinese_name']
            user['email'] = info['result'][0]['email']
            user['password'] = password

        return user

def check_reslut(user):
    try:
        if (user['status']):
            if (user['result'][0].has_key('english_name')
                and user['result'][0].has_key('chinese_name')
                and user['result'][0].has_key('email')):
                    return True
    except KeyError:
        pass
    except:
        pass

    return False

def login_with_oauth(request, client_id, client_secret, oauth_url) :
    if request.REQUEST.has_key('code') :
        data = {'client_id' : client_id, 'client_secret' : client_secret, 'grant_type' : 'authorization_code', 'code' : request.REQUEST['code']}
        outputstring = oauth_url+'/token.php?'+http_build_query(data)
        return outputstring

    if request.REQUEST.has_key('access_token') :
        access_token = request.REQUEST['access_token']
        data = {'oauth_token' : access_token}

        req = Request(oauth_url+'/resource.php', urlencode(data))
        raw_info = urlopen(req).read()
        info = json_decode(raw_info)

        if info :
            return info
        else :
            return False

    array = {'client_id' : client_id, 'response_type' : 'code'}
    outputstring = oauth_url+'/authorize.php?'+http_build_query(array)
    return outputstring

def http_build_query(data) :
    str = ''
    for k, v in enumerate(data) :
        str = str + v + '=' + data[v]
        if len(data)-1 > k :
            str = str + "&"
    return str

def get_info_from_ldap(access_token, oauth_url) :
    data = {'oauth_token' : access_token, 'getinfo' : True}

    req = Request(oauth_url+'/resource.php', urlencode(data))
    raw_info = urlopen(req).read()
    info = json_decode(raw_info)

    if info :
        return info
    else :
        return False

if __name__ == '__main__':
    pass

