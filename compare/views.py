# -*- coding: utf-8 -*-

from compare.models import Record
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404

import urllib2,difflib



#列表页获取所有记录
def index(request):
    records = Record.objects.all()
    return render_to_response('compare/index.html', {'records':records},)


#查看页面
def modify(request,rid):
    r = Record.objects.get(pk = rid)
    return render_to_response('compare/modify.html', {'r':r},)
    

#删除记录
def delete(request,rid):
    Record.objects.get(id = rid).delete()
    return HttpResponseRedirect("/compare/index")


#新增记录
def add(request):
    aurl = request.POST['aurl']
    burl = request.POST['burl']
    desc = request.POST['desc']
    astatus = request.POST['astatus']
    bstatus = request.POST['bstatus']
    diff = request.POST['diff']
    result = request.POST['result']
    Record.objects.create(aurl=aurl, burl=burl, desc=desc, astatus=astatus, bstatus=bstatus, diff=diff, result=result)
    return HttpResponseRedirect("/compare/index")          


#获取URL的内容
def getContent(request,x,rid):
    r = Record.objects.get(id = rid)
    try:
        if x == "a":
            r.acoutent = urllib2.urlopen(str(r.aurl)).read()
            r.astatus = 1
        elif x== "b":
            r.bcoutent = urllib2.urlopen(str(r.burl)).read()
            r.bstatus = 1
        r.save() 
    except ValueError:
        raise Http404("请确认URL是否合法")
    return HttpResponseRedirect("/compare/index") 



#比较HTML内容
def diff(request,rid):
    r = Record.objects.get(id = rid)
    if r.acoutent == r.bcoutent:
        r.result = 1
    else:
        tmp = difflib.unified_diff(str(r.acoutent).splitlines(),str(r.bcoutent).splitlines(),lineterm='')
        r.diff = '\n'.join(list(tmp))
        r.result = 2
    r.save()
    return HttpResponseRedirect("/compare/index") 
    
  
#清空单个操作记录  
def clear(request,rid):
    r = Record.objects.get(id = rid)
    r.astatus = 0
    r.bstatus = 0
    r.acoutent = ""
    r.bcoutent = ""
    r.result = 0
    r.diff = "无"
    r.save()
    return HttpResponseRedirect("/compare/index") 
    
    
#删除全部    
def delAll(request):
    Record.objects.all().delete()
    return HttpResponseRedirect("/compare/index") 

        
#清空全部
def clearAll(request):
    records = Record.objects.all()
    for r in records:
        r.astatus = 0
        r.bstatus = 0
        r.acoutent = ""
        r.bcoutent = ""
        r.result = 0
        r.diff = "无"
        r.save()
    return HttpResponseRedirect("/compare/index") 
        
