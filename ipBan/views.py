#encoding=utf8

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from libs.git import Git
import MySQLdb
import os
import json
import sys
import pycurl
import datetime
import time
from datetime import datetime
from time import mktime
from time import mktime as mktime
from django.contrib.auth.decorators import login_required
from account.decorators import group_required
from django.core.exceptions import ValidationError
from ipBan.models import *
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from auth.models import user_groups
from django.core.mail import send_mail
from django.http import HttpResponseRedirect  
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
import smtplib 
from django.db.models.query import QuerySet
from django.db.models.query import RawQuerySet
from django.db.models import Count 

reload(sys)   
sys.setdefaultencoding('utf8')  
@login_required(login_url='/login')
def list(request):
    data = {}
    data['type'] = int(request.GET.get('type'))
    data['page'] = int(request.GET.get('page')) if 'page' in request.GET else 1
    data['groupPage'] = int(request.GET.get('group_page')) if 'group_page' in request.GET else 1
    data['q'] = request.GET.get('q') if 'q' in request.GET else ''
    data['historyList'] = logList(__buildQuery(query=request.GET.get('q') if 'q' in request.GET else "",type=request.GET.get('type'),time1=1),request.GET['page'] if 'page' in request.GET else 1,request.GET.get('type'))
    data['groupList'] = logGroupList(__buildGroupQuery(query=request.GET.get('q') if 'q' in request.GET else "",type=request.GET.get('type'),time1=1),request.GET['group_page'] if 'group_page' in request.GET else 1)
    data['ruleList'] = ruleList()
    data['auth'] = getAuth(request.user.id,1)
    data['channelName'] = 'ipBan'
    return render(request, 'ipBan/list.html', {'data': data})

@login_required(login_url='/login')
def rule(request):
    data = {}
    data['monitorTypeList'] = logRuleList(__buildRuleQuery(query=request.GET.get('q') if 'q' in request.GET else ""))
    data['auth'] = getAuth(request.user.id,1)
    data['channelName'] = 'ipBan'
    return render(request, 'ipBan/rule.html', {'data': data})

@login_required(login_url='/login')
def ipInfo(request):
    data = {}
    data['q'] = request.GET.get('q') if 'q' in request.GET else ''
    data['white_page'] = int(request.GET.get('white_page')) if 'white_page' in request.GET else 1
    data['black_page'] = int(request.GET.get('black_page')) if 'black_page' in request.GET else 1
    data['whiteList'] = ipInfoList(__buildIpInfoQuery(query=request.GET.get('q') if 'q' in request.GET else "",is_white=1),request.GET['white_page'] if 'white_page' in request.GET else 1,request.GET['black_page'] if 'black_page' in request.GET else 1)
    data['blackList'] = ipInfoList(__buildIpInfoQuery(query=request.GET.get('q') if 'q' in request.GET else "",is_white=0),request.GET['black_page'] if 'black_page' in request.GET else 1,request.GET['black_page'] if 'black_page' in request.GET else 1)
    data['auth'] = getAuth(request.user.id,1)
    data['channelName'] = 'ipBan'
    return render(request, 'ipBan/ip_info.html', {'data': data})


def ajax(request):
    '''
    ajax统一请求入口
    通过标准action参数进行请求分发
    '''
    action = request.GET['action']
    if(action == 'update_rule_info'):
        responseInfo = updateRuleInfo(request.REQUEST,request.user)

    return HttpResponse(responseInfo)


def ruleList(type=""):
    ''' 
    封禁类型列表
    '''
    types = ParentType.objects.order_by('id')
    return types

def logList(q="",page=1,type=""):
    ''' 
    封禁ip列表
    '''
    if page == "":
        page = 1
    infos = Paginator(q.order_by('-id'), 15).page(page)
    for info in infos:
        info.created = time.strftime('%Y-%m-%d %X', time.localtime(info.created))
        info.type = getParentType(info.type)
        info.status=getIpStatus(info.ip)
    return infos

def logGroupList(q="",group_page=1,type=""):
    ''' 
    group列表
    '''
    infos = Paginator(q, 15).page(group_page)
    for info in infos:
        try:
            if info['type']:
                info['type'] = getParentType(info['type'])
        except:
            if type != 0:
                info['type'] = "总量"
            else:
                info['type'] = getParentType(info['type'])
        info['status']=getIpStatus(info['ip'])
    return infos

def logRuleList(q="",page=1,type=""):
    ''' 
    规则列表
    '''
    if page == "":
        page = 1
    infos = Paginator(q.order_by('id'), 15).page(page)
    for info in infos:
        info.desc = getParentType(info.parent_id)
    return infos

def ipInfoList(q="",white_page=1,black_page=1):
    ''' 
    规则列表
    '''
    infos = Paginator(q, 15).page(white_page)
    return infos

def getParentType(type=""):
    '''
    获取当前类型
    '''
    type = ParentType.objects.filter(id=type)[0]
    return type


def __buildQuery(query = '',type="", time1=0):
    if time1 == 1:
        time1=int(time.mktime(time.strptime(time.strftime("%Y%m%d", time.localtime()),'%Y%m%d')))
    if query == "":
        if type != "0":
            q = IpHistory.objects.filter(type=type,created__gte=time1)
        else:
            q = IpHistory.objects.filter(created__gte=time1)
    else:
        if type != "0":
            q = IpHistory.objects.filter(type=type,ip__contains=query,created__gte=time1)
        else:
            q = IpHistory.objects.filter(ip__contains=query,created__gte=time1)
    return q

def __buildGroupQuery(query = '',type="",time1=0):
    if time1 == 1:
        time1=int(time.mktime(time.strptime(time.strftime("%Y%m%d", time.localtime()),'%Y%m%d')))
    if query != "":
        q = IpHistory.objects.values('ip','type').filter(ip__contains=query,created__gte=time1).annotate(gcount=Count('ip')).order_by('-gcount')
    else:
        if type != "0":
            q = IpHistory.objects.values('ip','type').filter(type=type,created__gte=time1).annotate(gcount=Count('ip')).order_by('-gcount')
        else:
            q = IpHistory.objects.values('ip').filter(created__gte=time1).annotate(gcount=Count('ip')).order_by('-gcount')
    return q

def __buildRuleQuery(query = ''):
    if query == "":
        q = MonitorType.objects
    else:
        q = MonitorType.objects.filter(regex__contains=query)
    return q

def __buildIpInfoQuery(query = '',is_white = 0):
    if query == "":
        q = IpInfo.objects.filter(is_del=0 , is_white = is_white).order_by('ip')
    else:
        q = IpInfo.objects.filter(is_del=0,  is_white = is_white , ip__contains=query).order_by('ip')
    return q

def getIpStatus(ip=""):
    import pycurl
    import StringIO
    import urllib2
    url = "http://site-api.tj.a.ajkdns.com/tools/ip-shield/?act=getIpStatus&ip="+ip
    response = urllib2.urlopen(url)
    resultDict = json.load(response)
    status = resultDict['current_ip_is_black']
    return status

def getAuth(userId,groupId):
    '''
    获取权限
    '''
    try:
        user = user_groups.objects.filter(user_id=userId,group_id=groupId)[0]
        user_id = user.user_id
    except:
        user_id = 0
    return user_id

@login_required(login_url='/login')
def addIpHtml(request):
    '''
    增加ip库
    '''
    data = {}
    data['auth'] = getAuth(request.user.id,1)
    data['channelName'] = 'ipBan'
    return render(request, 'ipBan/add_ip.html', {'data': data})

@login_required(login_url='/login')
def addIp(request):
    ip = request.GET['ip']
    is_white = request.GET['is_white']
    desc = request.GET['desc']
    try:
        IpInfo.objects.filter(ip=ip)[0]
    except:
        generator = int(request.user.id)
        ipInfo = IpInfo(
        ip = ip,
        is_white = is_white,
        desc = desc,
        is_del = 0,
        generator = generator
        )
        ipInfo.save()
        if is_white == "0":
           shellPath = settings.SHELL_PATH
           os.popen(shellPath+"heimingdan.sh")
    return HttpResponseRedirect('/ipBan/ipInfo/')



@login_required(login_url='/login')
def addRuleHtml(request):
    '''
    增加ip库
    '''
    data = {}
    data['ruleList'] = ruleList()
    data['auth'] = getAuth(request.user.id,1)
    data['channelName'] = 'ipBan'
    return render(request, 'ipBan/add_rule.html', {'data': data})

@login_required(login_url='/login')
def addRule(request):
    parent_id = request.GET['parent_id']
    freq = request.GET['freq']
    num = request.GET['num']
    hostname = request.GET['hostname']
    regex = request.GET['regex']
    generator = int(request.user.id)
    monitorType = MonitorType(
    parent_id = parent_id,
    freq = freq,
    num = num,
    hostname = hostname,
    regex = regex,
    generator = generator
    )
    monitorType.save()
    return HttpResponseRedirect('/rule/')

@login_required(login_url='/login')
def updateIp(request):
    '''
    更改ip状态
    '''
    ipInfo = IpInfo.objects.get(id = int(request.GET['id']))
    is_white=request.GET['is_white'] if 'is_white' in request.GET else "9"
    is_del=request.GET['is_del'] if 'is_del' in request.GET else "9"
    if is_white != "9": 
        ipInfo.is_white = is_white
    if is_del != "9":
        ipInfo.is_del = is_del
    ipInfo.save()
    if is_white == "0":
       shellPath = settings.SHELL_PATH
       os.popen(shellPath+"heimingdan.sh")
    return HttpResponseRedirect('/ipBan/ipInfo/')

def updateRuleInfo(requestInfo , generator):
    '''
    更改规则
    '''
    id=requestInfo['id']
    parent_id=requestInfo['parent_id']
    rule = MonitorType.objects.get(id = id)
    parentType = ParentType.objects.get(id = parent_id)
    filed_name = requestInfo['name']
    info = requestInfo['info']
    if filed_name == "desc":
        parentType.desc = info
        parentType.save()
    elif filed_name == "freq":
        rule.freq = info
    elif filed_name == "num":
        rule.num = info
    elif filed_name == "hostname":
        rule.hostname = info
    elif filed_name == "regex":
        rule.regex = info
    elif filed_name == "ipduan_select":
        rule.ipduan_select = info
    elif filed_name == "ipduan_num":
        rule.ipduan_num = info
    rule.generator = generator
    rule.save()
    return "ok"

@login_required(login_url='/login')
def ipAdminHtml(request):
    '''
    增加ip库
    '''
    data = {}
    data['auth'] = getAuth(request.user.id,1)
    data['channelName'] = 'ipBan'
    return render(request, 'ipBan/admin.html', {'data': data})

