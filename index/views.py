#encoding=utf8
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from libs.git import Git
from django.contrib.auth.decorators import login_required
from account.decorators import group_required
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect

def index(request):
    '''  
	首页导航
    '''


    data = {}  
    data['channelName'] = 'index'
    return render(request, 'Nav.html', {'data': data})
