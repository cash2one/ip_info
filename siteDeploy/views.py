#encoding=utf8

from django.http import HttpResponse
from django.contrib.auth import authenticate, logout as user_logout
from libs.util.render import rendr
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login')
@rendr('index.html', 'home')
def home(request):
    return {}


@rendr('global/nofound.html', 'home')
def page404(request):
    return {}


@rendr('global/error.html', 'home')
def pageError(request):
    return {}


@rendr('user/login.html', 'home')
def loginSite(request):
    return {}


def userajax(request):
    responseInfo = ''
    params = request.REQUEST
    action = params['action']
    if ('submit' == action):
        responseInfo = submit_login_info(params, request)
    if ('logout' == action):
        responseInfo = logout_web_site(request)
    return HttpResponse(responseInfo)


def submit_login_info(params, request):
    import json
    userinfo = json.loads(params['data'])
    user = authenticate(username=userinfo['username'], password=userinfo['passwd'])

    if user is not None:
        if user.is_active:
            return 1
    else:
        return -1


def logout_web_site(request):
    user_logout(request)
    return 1
