#coding:utf8

#------------------------------------OAUTH--------------------------------------------#
#------------------------------------OAUTH--------------------------------------------#
#------------------------------------OAUTH--------------------------------------------#

from account.decorators import group_required
from account.ldap import authenticate as ldap_authenticate
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Template, Context
from symbol import try_stmt
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError
from warnings import catch_warnings
import urllib2

client_id = settings.CLIENT_ID
client_secret = settings.CLIENT_SECRET
oauth_url = settings.OAUTH_URL

def login(request):
    print "running~~~~"
    if request.REQUEST.has_key('next'):
        thisUrl = request.path+"?next="+request.REQUEST['next']
    else:
        thisUrl = request.path

    from account.ldap import login_with_oauth
    outputstring = login_with_oauth(request, client_id, client_secret, oauth_url)
    if isinstance(outputstring, basestring) :
        return HttpResponseRedirect(outputstring)
    else :
        username = outputstring['username']
        access_token = outputstring['access_token']

    if len(User.objects.filter(username=username)) == 0:
        from account.ldap import get_info_from_ldap
        ldap_user = get_info_from_ldap(access_token, oauth_url)
        user = User.objects.create_user(username=ldap_user['username'], email=ldap_user['email'], password='aifang')
        user.is_staff = True
        user.first_name = ldap_user['chinese_name']
        user.save()

    user = auth.authenticate(username=username, password='aifang')

    thisUrl = '/'
    if user:
        auth.login(request, user)
        return HttpResponseRedirect(thisUrl)
    else:
        return HttpResponseRedirect(thisUrl)


def logout(request):
    from django.contrib.auth import authenticate, logout as user_logout
    user_logout(request)
    auth.logout(request)
    ref = 'http://home.corp.anjuke.com'
    url_get = '%s/logout.php?client_id=%s&client_secret=%s&refer_url=%s' % (oauth_url,client_id,client_secret,ref)
    req = urllib2.Request(url_get)
    try:
        response = urllib2.urlopen(req)
    except HTTPError,e:
        print e
        return None
    return HttpResponseRedirect("/")
    
