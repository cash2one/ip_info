#encoding=utf8
from django.contrib.auth.decorators import login_required
from libs.util.render import rendr
from project.models import Cate, Project, Design, DesignAttach
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import json
import time
from project.services import cateModule

CHANNEL = 'project'
NOT_FOUND_PAGE = 'global/nofound.html'
DESIGN_FLAG_SAVE = 0 #保存
DESIGN_FLAG_COMPLETE = 1 #完成


@login_required(login_url='/login')
@rendr('project/home.html', CHANNEL)
def catelist(request):
    '''
    分类
    '''
    dom = getTreeDom(None)
    return render(request, 'project/cate/list.html', {'data':dom})

'''
获取子类dom
'''
def getTreeDom(cate):
    dom = '<ul>'
    if cate == None:
        param = 0
    else:
        param = cate.id
    children = Cate.objects.filter(parentId=param, status=0).order_by("id")
    
    if len(children) == 0:
        return ''
    
    for c in children:
        bootstrapAttribute = "data-toggle='modal' data-target='#myModal'"
        action = "<a class='add' " + bootstrapAttribute + ">+</a><a class='delete'>-</a><a class='edit' data-toggle='modal'>i</a>"
        dom += '<li cid=%s><i></i><span>%s</span>%s %s</li>'  %(c.id,c.name,action,getTreeDom(c)) 
    dom +='</ul>'
    return dom


@login_required(login_url='/login')
@rendr('project/home.html', CHANNEL)
def cateadd(request):  
    name = request.REQUEST.get('cate', None)
    if name == None:
        return render(request, NOT_FOUND_PAGE)
    
    cid = request.REQUEST.get('cid')
    if len(cid) == 0:
        cid = 0
    #更新
    if request.REQUEST.get('operate') == "1":
        cate = Cate.objects.get(id=cid)
        cate.name = name
    else:#添加
        cate = Cate(name=name, parentId=cid, status=0)
    cate.save()
    return HttpResponseRedirect('list')

@login_required(login_url='/login')
@rendr('project/home.html', CHANNEL)
def catedelete(request):
    cid = request.REQUEST.get('cid', None)
    children = Cate.objects.filter(parentId=cid, status=0)
    
    if len(children) != 0:
        requestInfo = json.dumps({'status':1, 'msg':'请先删除子类'})
        return HttpResponse(requestInfo)
    
    cate = Cate.objects.get(id=cid)
    cate.status = 1
    cate.save()
    requestInfo = json.dumps({'status':0, 'msg':'删除成功'})
    return HttpResponse(requestInfo)
'''
获取子功能块
'''
def catechildrenlist(request):
    pid = request.REQUEST.get('pid', None)
    if len(pid) == 0:
        requestInfo = json.dumps({'status':2, 'msg':'参数错误'})
        return HttpResponse(requestInfo)
    
    catelist = Cate.objects.filter(parentId=pid, status=0)
    if catelist:
        res = []
        for cate in catelist:
            item = {}
            item['id'] = cate.id
            item['name'] = cate.name
            res.append(item)
        requestInfo = json.dumps({'status':0, 'list':res})
    else:
        requestInfo = json.dumps({'status':1, 'msg':'没有子类'})
    return HttpResponse(requestInfo)

'''
项目设计CRUD
'''
@login_required(login_url='/login')
@rendr('project/home.html', CHANNEL)
def designcreate(request, projectId):
    if projectId == None:
        return render(request, NOT_FOUND_PAGE)
    
    # 判断该项目是否存在 如过不存在 跳转到404页面
    try:
        plist = Project.objects.get(pk=projectId)
    except Project.DoesNotExist:
        return render(request, NOT_FOUND_PAGE)
    
    if request.method == 'GET':#显示创建页面
        try:
            model = Design.objects.get(project=plist)
        except Design.DoesNotExist:
            model = None
        cm = cateModule()
        #获取功能块 DOM
        cateList = cm.getCateListByProjectId(projectId)
        cateListDom = '' if cateList==None else cateList
        topCate = cm.getCateByParentId(0)
        #获取附件
        attachList = DesignAttach.objects.filter(project=plist,status=0)
        return render(request, 'project/design/create.html', {'plist':plist,'design':model,'topCate':topCate, 'cateListDom':cateListDom,'attachList':attachList})
    else: #提交数据
        content = request.REQUEST.get('content')
        complete_flag = DESIGN_FLAG_SAVE if request.REQUEST.get('save_action') != None else DESIGN_FLAG_COMPLETE
        now = time.strftime("%Y-%m-%d %X", time.localtime())
        cm = cateModule()
        try: #更新
            #更新项目设计
            design = Design.objects.get(project=plist)
            design.content = content
            design.updated = now
        except Design.DoesNotExist:#插入
            #插入项目设计
            design = Design(project=plist, content=content, complete=complete_flag, status=0, creater=request.user.id, created=now, updated=now)
        design.save()
        #更新功能块
        catelist = request.REQUEST.getlist('cate')
        if catelist == None:
            pass
        else:#插入功能块:
            cm.replaceProjectCate(projectId,catelist,request.user.id)
        #上传附件
        filelist = request.FILES.getlist('design_files') if 'design_files' in request.FILES else None
        if filelist == None:
            pass
        else:#插入附件:
            cm.createDesignAttach(projectId,filelist,request.user.id)
        return HttpResponseRedirect('/project/design/detail/%d/' % int(projectId))
    

@rendr('project/home.html', CHANNEL)
def designdetail(request, projectId):
    if projectId == None:
        return render(request, NOT_FOUND_PAGE)
    try:
        plist = Project.objects.get(pk=projectId)
        design = Design.objects.get(project=plist)
        cm = cateModule()
        cateList = cm.getCateListByProjectId(projectId,False)
        cateListDom = '' if cateList==None else cateList
        #获取附件
        attachList = DesignAttach.objects.filter(project=plist,status=0)
        if design != None:
            return render(request, 'project/design/detail.html', {'design':design,'cateListDom':cateListDom,'attachList':attachList})
    except Project.DoesNotExist:
        return render(request, NOT_FOUND_PAGE)
    return render(request, NOT_FOUND_PAGE)
    
@login_required(login_url='/login')
@rendr('project/home.html', CHANNEL)
def designdelete(request, projectId):
    if projectId == None:
        return render(request, NOT_FOUND_PAGE)

@login_required(login_url='/login')
@rendr('project/home.html', CHANNEL)
def deleteattach(request, attachId):
    if attachId == None:
        return render(request, NOT_FOUND_PAGE)
    else:
        try:
            attach = DesignAttach.objects.get(pk=attachId)
        except Design.DoesNotExist:#插入
            return render(request, NOT_FOUND_PAGE)
        attach.status=1
        attach.save()
        return HttpResponseRedirect('/project/design/create/%d/' % int(attach.project_id))
    
    
