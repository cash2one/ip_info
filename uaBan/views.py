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
from uaBan.models import *
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
def uaInfo(request):
    data = {}
    data['q'] = request.GET.get('q') if 'q' in request.GET else ''
    data['list'] = uaInfoList(__buildUaInfoQuery(query=request.GET.get('q') if 'q' in request.GET else ""),request.GET['page'] if 'page' in request.GET else 1)
    data['auth'] = getAuth(request.user.id,1)
    data['channelName'] = 'ipBan'
    return render(request, 'uaBan/ua_info.html', {'data': data})

def uaInfoList(q="",page=1):
    ''' 
    规则列表
    '''
    infos = Paginator(q, 15).page(page)
    return infos

def __buildUaInfoQuery(query = ''):
    if query == "":
        q = UaInfo.objects.filter(is_del=0 ).order_by('id')
    else:
        q = UaInfo.objects.filter(is_del=0, user_agent__contains=query).order_by('id')
    return q
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
def addUaHtml(request):
    '''
    增加user agent库
    '''
    data = {}
    data['auth'] = getAuth(request.user.id,1)
    data['channelName'] = 'uaBan'
    return render(request, 'uaBan/add_ua.html', {'data': data})

@login_required(login_url='/login')
def addUa(request):
    user_agent = request.GET['user_agent']
    try:
        UaInfo.objects.filter(user_agent=user_agent)[0]
    except:
        generator = int(request.user.id)
        uaInfo = UaInfo(
        user_agent = user_agent,
        is_del = 0,
        generator = generator
        )
        uaInfo.save()
    return HttpResponseRedirect('/uaBan/uaInfo/')

@login_required(login_url='/login')
def updateUa(request):
    '''
    更改user agent状态
    '''
    uaInfo = UaInfo.objects.get(id = int(request.GET['id']))
    is_del=request.GET['is_del'] if 'is_del' in request.GET else "9"
    if is_del != "9":
        uaInfo.is_del = is_del
    uaInfo.save()
    return HttpResponseRedirect('/uaBan/uaInfo/')
