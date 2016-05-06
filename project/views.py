#encoding=utf-8

\
import json
import datetime
import threading
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import connection
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.timezone import utc
from libs.git import Git
from libs.ibug import Ibug
from libs.pmt import Pmt
from libs.util.render import rendr
from libs.util import locker
from django.contrib.auth.models import User
from webgit.models import Fp
from deploy.models import BranchInfo
from account.decorators import group_required
from project.forms import NewProject, MemoForm ,DelayForm 
from project.models import Project, Branch, RelatedPerson, Design, Memo, ProjectTime, weekreports, Tasktime ,DelayInfo
from project.services import ProjectModule, MemoModule,InsertInfo

CHANNEL = 'project'
NOT_FOUND_PAGE = 'global/nofound.html'

PROJECT_STATUS_CLASSES = {
    1: 'label-warning label-chinese',    # 待开发
    2: 'label-success label-chinese',    # 正在开发
    3: 'label-info label-chinese',       # 正在测试
    4: 'label-important label-chinese',  # 待合并
    5: 'label-inverse label-chinese',    # 待上线
    6: 'label-chinese'                   # 已上线
}


@login_required(login_url='/login')
def updateHtml(request):
    data = {}
    data['list'] = info(request.GET.get('id'))
    data['bname'] = bname(request.GET.get('id'))
    data['form'] = NewProject(initial={'createPerson': request.user.first_name})
    return render(request, 'project/update.html', {
        'data':data
    })

def delayHtml(request):
    data = {}
    data['form'] = DelayForm()
    data['id'] = request.GET.get('id')
    return render(request, 'project/delay.html', {
        'data':data
    })

def success(request):
    return render(request, 'project/success.html') 

def info(id):
    list = Project.objects.filter(id = id)
    return list

def bname(id):
    list = Branch.objects.filter(project = id)
    return list

def add_delay(request):
    import urllib2
    plist_id = request.GET['id']
    onlineDate = request.GET['onlineDate']
    delayDate = request.GET['delayDate']
    person = request.GET['person']
    person = person.replace("，",",")
    delayReason = request.GET['delayReason']
    try:
        b = DelayInfo.objects.get(plist_id = plist_id)
        b.delete()
    except:
        pass
    delayInfo = DelayInfo(
    plist_id = plist_id,
    onlineDate = onlineDate,
    delayDate = delayDate,
    person = person,
    delayReason = delayReason
    )   
    delayInfo.save()
    project = Project.objects.get(pk=plist_id)
    project.delay = 1 
    project.save()
    return HttpResponseRedirect('/project/success')

#@login_required(login_url='/login')
def update_remote(requestInfo):
    id = requestInfo['projectId']
    remote = requestInfo['remote']+","
    branch = requestInfo['branch']
    p = Project.objects.get(id=id)
    p.remote = remote
    p.save()
    Git.createBranch(branch,'master',0,remote)
    InsertInfo.insert(branch,remote,id,p.status)


@login_required(login_url='/login')
@rendr('project/home.html', CHANNEL)
def projects(request):
    '''
    项目列表
    '''
    searching = True if request.GET.get('q') else False
    q = __buildQuery(query=request.GET.get('q', ''))

    projects, pager = ProjectModule.getProjects(q=q, page=request.GET.get('page', '1'))

    return {
        'projects': projects,
        'pager': pager,
        'project_statuses': PROJECT_STATUS_CLASSES,
        'tab': '' if searching else 'all',
    }

@login_required(login_url='/login')
@rendr('project/home.html', CHANNEL)
def pendingProjects(request, type):
    '''
    某段时间上线项目
    '''
    if type not in ['today', 'tomorrow', 'week','delayed']:
        return redirect('/nofound')

    q = __buildQuery(day=type)
    projects, pager = ProjectModule.getProjects(q=q, page=request.GET.get('page', '1'))

    return {
        'projects': projects,
        'pager': pager,
        'project_statuses': PROJECT_STATUS_CLASSES,
        'tab': type,
    }

@login_required(login_url='/login')
@rendr('project/home.html', CHANNEL)
def archivedProjects(request):
    '''
    已归档的项目
    '''
    q = __buildQuery(archived=True)
    projects, pager = ProjectModule.getProjects(q=q, page=request.GET.get('page', '1'))

    return {
        'projects': projects,
        'pager': pager,
        'project_statuses': PROJECT_STATUS_CLASSES,
        'tab': 'archive',
    }

@login_required(login_url='/login')
@rendr('project/home.html', CHANNEL)
def myProjects(request):
    '''
    我的项目
    '''
    q = __buildQuery(user=User.objects.get(id=request.user.pk))

    projects, pager = ProjectModule.getProjects(q=q, page=request.GET.get('page', '1'))

    return {
        'projects': projects,
        'pager': pager,
        'project_statuses': PROJECT_STATUS_CLASSES,
        'tab': 'my',
    }

@login_required(login_url='/login')
@rendr('project/home.html', CHANNEL)
def modifyOnlineDate(request):
    if request.method == 'GET':
        return render(request, NOT_FOUND_PAGE)

    from_url = request.META['HTTP_REFERER'];
    pid = request.REQUEST.get('pid')
    newDate = request.REQUEST.get('newDate')
    if len(pid) == 0:
        return render(request, NOT_FOUND_PAGE)

    project = ProjectModule.getProject(pid)
    project.onlineDate = newDate
    project.save()
    return HttpResponseRedirect(from_url)

@login_required(login_url='/login')
@rendr('project/create.html', CHANNEL)
def create(request):
    '''
    创建项目
    '''

    if request.method == 'POST':
        form = NewProject(request.POST)
        if form.is_valid():
            projectId = ProjectModule.create(data=form.cleaned_data, user=request.user)
            return redirect("/project/detail/%d#cb" % projectId)
    else:
        form = NewProject(initial={'createPerson': request.user.first_name})

    #多人开发的有效可用pmt主分支
    parent_list = Project.objects.filter(pmtType=2, status__lt=6, type=1)

    return {
        'form': form,
        'parent_list': parent_list,
    }


def display_meta(request):
    '''
    display_meta
    '''
    values = request.META.items()
    values.sort()
    html = []
    for k, v in html:
        html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, v))
    return HttpResponse('<table>%s</table>' % '\n' . join(html))

@login_required(login_url='/login')
@rendr('project/viewDetail.html', CHANNEL)
def viewDetail(request, projectId):
    '''
    查看详情页
    '''
    project = ProjectModule.getProject(projectId=projectId)
    project.barClass = 'bar-danger' if project.type == 2 else 'bar-normal'
    branch_info = BranchInfo.objects.filter(plist_id=projectId)
    for subproject in project.subprojects:
        subproject.barClass = 'bar-danger' if subproject.type == 2 else 'bar-normal'


    return {
        'branch_name': project.branch_name,
        'project': project,
        'bugs': project.bugs,
        'gitlogs': project.gitlogs,
        'description': project.description,
        'memos': project.memos,
        'staffs': project.relatedPersons,
        'pgurl': project.branch_name+".anjuke.test",
    }


def getPlanTime(p, tasks, ptask=0):
    '''
    获得计划测试和开发时间
    '''
    if tasks == 0:
        p.dev_plan_end = ptask[0].devtime
        p.test_plan_end = ptask[0].testtime
        p.if_need_dev = ptask[0].ifNeedDev
        p.ex_test = ptask[0].exTest
    else:
        dev_plan_ends = []
        test_plan_ends = []
        dev_plan_ends = [t['date_end_plan'] for t in tasks if t['task_type_id'] in ['2', '3']]
        test_plan_ends = [t['date_end_plan'] for t in tasks if t['task_type_id'] in ['4']]
        p.dev_plan_end = max(dev_plan_ends) if len(dev_plan_ends) > 0 else ''
        p.test_plan_end = max(test_plan_ends) if len(test_plan_ends) > 0 else ''
    return p


def getFactTime(p, p_list,):
    '''
    获得实际测试和开发时间
    '''
    for pp in p_list:
        #需要开发和测试
        #改时区
        pp.time = pp.time + datetime.timedelta(hours=8)
        if (p.if_need_dev == 1 and p.if_need_test == 1):
            if pp.status == 3:
                p.dev_fact_end = str(pp.time)[0:10]
            elif pp.status == 4:
                p.test_fact_end = str(pp.time)[0:10]
        #需要开发，不需要测试
        elif(p.if_need_dev == 1 and p.if_need_test == 0):
            if pp.status == 4:
                p.dev_fact_end = str(pp.time)[0:10]
        #不需要开发，需要测试
        elif(p.if_need_dev == 1 and p.if_need_test == 1):
            if pp.status == 4:
                p.test_fact_end = str(pp.time)[0:10]
    return p


def ifDelay(p):
    '''
    计算项目是否延期
    '''
    #项目状态:0.normal 1.开发延期2.测试延期3.开发和测试延期4.异常
    p.pmtstatus = 0
    p.presultAlias = ''
    #是否需要开发和测试：1.需要；0.不需要
    if (p.if_need_dev == 1 and p.if_need_test == 1):
        if (p.dev_plan_end == '' or p.test_plan_end == '' or p.ex_test == 0):
            p.pmtstatus = 4
        else:
            #项目正常
            if (p.dev_plan_end >= p.dev_fact_end and p.test_plan_end >= p.test_fact_end and
                p.dev_fact_end != '' and p.test_fact_end != ''):
                p.pmtstatus = 0
            else:
                #开发延期
                if (p.dev_plan_end < p.dev_fact_end or p.dev_fact_end == ''):
                    p.pmtstatus += 1
                #测试延期
                if (p.test_plan_end < p.test_fact_end or p.test_fact_end == ''):
                    p.pmtstatus += 2
    elif(p.if_need_dev == 1 and p.if_need_test == 0):
        if (p.dev_plan_end == '' or p.test_plan_end <> '' or p.ex_test == 1):
            p.pmtstatus = 4
            p.test_fact_end = ''
            p.test_plan_end = ''
        else:
            #项目正常
            if (p.dev_plan_end >= p.dev_fact_end and
                p.dev_fact_end <> '' and p.test_fact_end == ''):
                p.pmtstatus = 0
            #开发延期
            if (p.dev_plan_end < p.dev_fact_end or p.dev_fact_end == ''):
                p.pmtstatus += 1
            #出现多余测试时间
            if ( p.test_fact_end <> ''):
                p.pmtstatus = 4
            p.test_fact_end = '无需测试'
            p.test_plan_end = '无需测试'
    elif(p.if_need_dev == 0):
        #有异常
        p.pmtstatus = 4
    return p

def getPMTResult(p,project_type):
    '''
    根据PMT计算结果得出结论
    '''
    #正常
    if (p.pmtstatus == 0):
        p.presult = 2
        p.presultAlias = '项目正常'
        project_type[3] += 1
    #异常
    else:
        project_type[0] += 1
        if(p.pmtstatus == 1):
            p.presult = 3
            p.presultAlias = '开发延期'
            project_type[1] += 1
        elif(p.pmtstatus == 2):
            p.presult = 4
            p.presultAlias = '测试延期'
            project_type[2] += 1
        elif(p.pmtstatus == 3):
            p.presult = 1
            p.presultAlias = '开发和测试延期'
            project_type[1] += 1
            project_type[2] += 1
        #纯异常
        elif(p.pmtstatus == 4):
            p.presult = 5
            p.presultAlias = '项目异常'
    return p,project_type

def queryPMTdate(p, project_type,time_list,ttime):
    '''
    查询PMT项目数据
    '''
    p.summary = str(p.relatedId) + ' - ' + p.name
    p.ex_test = 0
    p.test_fact_end = ''
    p.dev_fact_end = ''
    p.if_need_dev = 0
    p.if_need_test = 0
    p_list = time_list.filter(project = p.id)
    #未上线不读数据库
    if p.status != 6:
        tasks = Pmt().getTaskInfoByProjectId(p.relatedId)
        for need in tasks:
            if (int(need['task_type_id']) == 3 or int(need['task_type_id']) == 2):
                p.if_need_dev = 1
            if p.testType == 1:
                p.if_need_test = 1
            if (int(need['task_type_id']) == 4):
                p.ex_test = 1
        p = getPlanTime(p,tasks)
    #已上线，读或者写数据库
    else:
        ptask = ttime.filter(relatedId = p.relatedId)
        if len(ptask) > 0:
            if p.testType == 1:
                p.if_need_test = 1
            p = getPlanTime(p,0,ptask)
        else:
            tasks = Pmt().getTaskInfoByProjectId(p.relatedId)
            for need in tasks:
                if (int(need['task_type_id']) == 3 or int(need['task_type_id']) == 2):
                    p.if_need_dev = 1
                if p.testType == 1:
                    p.if_need_test = 1
                if (int(need['task_type_id']) == 4):
                    p.ex_test = 1
            p = getPlanTime(p,tasks)
            Tasktime(relatedId = p.relatedId,devtime = str(p.dev_plan_end) ,
                    testtime = str(p.test_plan_end),exTest = p.ex_test,
                    ifNeedDev = p.if_need_dev).save()

    p = getFactTime(p,p_list)
    p = ifDelay(p)
    p, project_type = getPMTResult(p,project_type)
    return p,project_type

def getHotfixResult(p,project_type,process,ibug):
    '''
    计算Hotfix结果得出结论
    '''
    #改时区
    p.created_at1 = p.created_at1.replace(tzinfo=utc) + datetime.timedelta(hours = -8)
    p.presult = 2
    update_fact_at = ''
    if  p.created_at1 <> '' and  process <> None :
        update_fact_at = process.time
        day_sub = (update_fact_at - p.created_at1).days
        # 一天内完成
        if day_sub == 0:
            project_type[1] += 1
            p.presult = 2
            p.presultAlias = '24小时完成'
        # 两天内完成
        elif day_sub == 1:
            project_type[2] += 1
            p.presult = 3
            p.presultAlias = '48小时完成'
        # 两天后完成
        elif day_sub > 1:
            project_type[3] += 1
            project_type[0] += 1
            p.presult = 4
            p.presultAlias = '未48小时完成'
        else:
            project_type[0] += 1
            p.presult = 5
            p.presultAlias = '项目异常'
    elif(p.created_at <> '' and  process == None):
        #未完成
        project_type[3] += 1
        project_type[0] += 1
        p.presult = 4
        p.presultAlias = '未48小时完成'
    else:
        #异常数
        project_type[0] += 1
        p.presult = 5
        p.presultAlias = '项目异常'
    p.processed_at = update_fact_at
    return p,project_type

def queryHotfixdate(p,ibug,time_list,project_type = [0,0,0,0]):
    '''
    查询Hotfix项目数据
    '''
    process = None
    if ibug is None :
        p.created_at = ''
    else:
        p.summary = str(p.relatedId) + ' - ' + p.name
        p.created_at = ibug['created_at']
        created_at_year = int(p.created_at[0:4])
        created_at_mon = int(p.created_at[5:7])
        created_at_day = int(p.created_at[8:10])
        created_at_hour = int(p.created_at[11:13])
        p.created_at1 = datetime.datetime(created_at_year,created_at_mon,created_at_day,
                               created_at_hour,0,0)


    #获得实际修改时间
    for pt in time_list :
        if pt.status == 4 and pt.project.id == p.id:
            process = pt
    p,project_type = getHotfixResult(p,project_type,process,ibug)
    return p,project_type

def initWeekReportTable(weekneed):
    '''
    初始化数据库数据
    '''
    #过滤掉不需要的数据
    weeklist = getweek()
    pmtlist, hotfixlist = getsource(weeklist)
    source = [[0 for ii in range(0,8)] for i in range(0,weekneed)]
    now = datetime.datetime.now()
    lastdate = now + datetime.timedelta(days = -90)
    factdata = ProjectTime.objects.filter(time__gte = lastdate)
    for i in range(0,weekneed):
        project_list = []
        for p in pmtlist:
            if p.weeknum1 == weeklist[9 - i]:
                project_list.append(p)
        if len(project_list) > 0:
            source[i][0:4] = pmtdeal(project_list,factdata)
        else:
            source[i][0:4] = [0,0,0,0]
        project_list = []
        for p in hotfixlist:
            if p.weeknum1 == weeklist[9 - i]:
                project_list.append(p)
        if len(project_list) > 0:
            source[i][4:8] = hotfixdeal(project_list,factdata)
        else:
            source[i][4:8] = [0,0,0,0]
    weeklist = getweek(1)
    for i,weekdata in zip(range(0,weekneed),source):
        for tt in range(1,9):
            pt = weekreports(type = tt, weeknum = weeklist[9 - i], num = weekdata[tt - 1])
            pt.save()

def pmtdeal(weekdata,factdata):
    '''
    处理pmt项目
    '''
    project_type = [0,0,0,0]
    ids = [p.id for p in weekdata]
    time_list = factdata.filter(project__in = ids)
    relatedIds = [p.relatedId for p in weekdata]
    ttime = Tasktime.objects.filter(relatedId__in = relatedIds)

    for p in weekdata:
        p, project_type = queryPMTdate(p,project_type,time_list,ttime)
    return project_type

def hotfixdeal(weekdata,factdata):
    '''
    处理hotfix项目
    '''
    project_type = [0,0,0,0]
    p_relatedIds = [int(p.relatedId) for p in weekdata]
    p_ids = [int(p.id) for p in weekdata]
    time_list = factdata.filter(project__in = p_ids)
    ibugs = Ibug().getDetailInfoById(p_relatedIds)
    for p,ibug in zip(weekdata,ibugs):
        p, project_type = queryHotfixdate(p,ibug,time_list,project_type)
    return project_type

@login_required(login_url = '/login')
@group_required(group = 'stageman')
def reports(request):
    '''
    项目报告
    '''
    weeksnum = []
    weeklist = getweek(1)
    all_data = weekreports.objects.order_by('-weeknum').all()[:10]
    if len(all_data) > 0 and all_data[0].weeknum in weeklist:
        weekneed = 9 - weeklist.index(all_data[0].weeknum)
    else:
        weekneed = 10
    if weekneed > 0:
        initWeekReportTable(weekneed)
    weeklist = getweek()
    source = getdata()
    source = dealdata(source)
    return render(request, 'project/reports.html', {'data': {
        'source1':source,
        'weeksnum':weeklist,
    }})

def getweek(flag = 0):
    '''
    计算所需要的10周的周数数字
    '''
    today = datetime.date.today()
    y1 = int(str(today)[0:4])
    y2 = y1 - 1
    thisweek = int(today.strftime('%W'))
    if thisweek >= 11:
        weeklist = [i  for i in range(thisweek - 10, thisweek)]
        yweeklist = [i + y1*100  for i in weeklist]
    else:
        weeklist1 = [i  for i in range(1, thisweek)]
        yweeklist1 = [i + y1*100  for i in weeklist1]
        todaynum = int(today.strftime('%j'))
        lastyear = today + datetime.timedelta(days = -todaynum)
        lastyearnum = int(lastyear.strftime('%W'))
        weeklist2 = [i for i in range(lastyearnum + thisweek - 10, lastyearnum + 1)]
        yweeklist2 = [i + y2*100  for i in weeklist2]
        weeklist = weeklist2 + weeklist1
        yweeklist = yweeklist2 + yweeklist1
    if flag == 0:
        return  weeklist
    else:
        return  yweeklist

def getdata():
    '''
    从数据库中读取数据
    '''
    #计算所需要的10周数字
    weeklist = getweek(1)
    source = [[0 for ii in range(0,8)] for i in range(0,10)]
    all_data = weekreports.objects.order_by('-weeknum').all()
    for i,w in zip(range(0,10),weeklist):
        for tt in range(1,9):
            p = all_data.filter(weeknum = w ,type = tt)
            source[i][tt-1] = p[0].num
    return source

def dealdata(s):
    '''
    按照输出要求处理数据格式
    '''
    tlist = [[] for i in range(0,8)]
    for i in range(0,10):
        for t in range(0,8):
            tlist[t].append(s[i][t])
    datadict = {'exceptNum':tlist[0],'devLateNum':tlist[1],'testLateNum':tlist[2],
                'normalPMTNum':tlist[3],'fixInOneDay':tlist[5],'fixInTwoDay':tlist[6],
                'fixOutTwoDay':tlist[7],'exceptHotfixs':tlist[4],}
    return datadict

def getsource(wlist):
    '''
    获取需要的原始数据
    '''
    today = datetime.date.today()
    todaynum = int(today.strftime('%j'))
    lastyear = today + datetime.timedelta(days = -todaynum)
    lastyearnum = int(lastyear.strftime('%W'))
    temm = today + datetime.timedelta(days = -90)
    all_data = Project.objects.filter(onlineDate__gte = temm,
                                      onlineDate__lte = today,archived = 0)
    #过滤掉不需要的数据
    weeklist = wlist

    owners = User.objects.all()
    #mylist:1.pmt project,2.hotfix project
    pmtlist, hotfixlist = [], []
    for p in all_data:
        #增加一个周数的属性
        p.weeknum1 = int(p.onlineDate.strftime('%W'))
        p.weeknum1 = p.weeknum1 if p.weeknum1 <> 0 else  lastyearnum
        p.owner = owners.get(id=p.createPerson)
        #此项目为PMT项目
        if  p.weeknum1 in wlist and p.type == 1:
            pmtlist.append(p)
        #此项目为hotfix项目
        if  p.weeknum1 in wlist and p.type == 2:
            hotfixlist.append(p)
    return pmtlist,hotfixlist

def getweeknear(weekNum):
    weeklist = getweek()
    lowflag = weeklist.index(weekNum)
    pre , next = 1,1
    if lowflag == 0:
        pre = 0
    elif lowflag == 9:
        next = 0
    preweek = str(weekNum - 1)
    nextweek = str(weekNum + 1)
    wdict = {'pre':pre, 'next':next, 'preweek':preweek,
             'nextweek':nextweek,'weekNum':weekNum}
    return wdict

def reportsflash(request):
    '''
    刷新数据库数据
    '''
    return redirect("/project/reports/")

@login_required(login_url = '/login')
@group_required(group = 'stageman')
def report(request,weekNum):
    '''
    显示指定一周项目情况
    '''
    weekNum = int(weekNum)
    pmtlist, hotfixlist = getsource([weekNum,])
    project_ids = [p.id for p in pmtlist]
    bug_ids = [p.id for p in hotfixlist]
    bug_relatedIds = [p.relatedId for p in hotfixlist]
    pmt_relatedIds = [p.relatedId for p in pmtlist]
    now = datetime.datetime.now()
    lastdate = now + datetime.timedelta(days = -90)
    factdata = ProjectTime.objects.filter(time__gte = lastdate)
    ibugs = Ibug().getDetailInfoById(bug_relatedIds)
    ttime = Tasktime.objects.filter(relatedId__in = pmt_relatedIds)
    dd = [0,0,0,0]
    for p in hotfixlist:
        ibug = None
        for data in ibugs:
            if (p.relatedId == int(data['id'])):
                ibug = data
        p, dd = queryHotfixdate(p,ibug,factdata,dd)
    for p in pmtlist:
        p, dd = queryPMTdate(p,dd,factdata,ttime)
    weeknear = getweeknear(weekNum)
    return render(request, 'project/report.html', {'data': {
        'bugs': hotfixlist,
        'projects': pmtlist,
        'weeknear':weeknear,
        'project_statuses': PROJECT_STATUS_CLASSES,
    }})


@login_required(login_url='/login')
@rendr('project/createMemo.html', CHANNEL)
def createMemo(request, projectId):
    '''
    创建上线备忘
    '''
    # 判断该项目是否存在 如过不存在 跳转到404页面
    try:
        plistModel = Project.objects.get(pk=projectId)
    except Project.DoesNotExist:
        return render(request, 'global/nofound.html')

    # 判断是显示页面还是插入数据
    if request.method == 'POST':
        # 插入数据操作
        typeList = request.POST.getlist('type')
        contentList = request.POST.getlist('content')
        # 循环插入数据
        branch_info = BranchInfo.objects.filter(title = plistModel.name) 
        for (offset, item) in enumerate(typeList):
            if contentList[offset]:
                memo = Memo(project=plistModel, type=item, content=contentList[offset], done=0)
                memo.save()
            for bi in branch_info:
                if str(item) == '7': 
                    bi.if_jockjs = 1
                if str(item) == '8': 
                    bi.if_pages = 1
                if str(item) == '13':
                    bi.desc = contentList[offset]
                bi.save()
        return redirect("/project/detail/%s/" % projectId)
    else:
        # 显示页面
        return {
            'form': MemoForm(),
            'id': projectId,
        }


@login_required(login_url = '/login')
@rendr('project/modifyMemo.html', CHANNEL)
def modifyMemo(request, projectId):
    '''
    修改上线备忘
    '''
    plistModel = Project.objects.get(pk=projectId)
    memoList = Memo.objects.filter(project=plistModel).all()

    # 判断是显示页面还是插入数据
    if request.method == 'POST':
        #修改数据操作
        typeList = request.POST.getlist('type')
        contentList = request.POST.getlist('content')
        memoIdList = request.POST.getlist('memoId')

        #删除删掉的数据
        for delMemo in memoList:
            if str(delMemo.pk) not in memoIdList:
                delMemo.delete()

        #循环插入数据
        branch_info = BranchInfo.objects.filter(title = plistModel.name) 
        for bi in branch_info:
            bi.if_jockjs = 0
            bi.if_pages = 0
            bi.desc = ""
            bi.save()

        for (offset, item) in enumerate(typeList):
#            if len(memoIdList) < offset:  #对数据进行更新
            if memoIdList[offset]:  # 对数据进行更新
                memo = Memo(pk=memoIdList[offset], project=plistModel, type=item, content=contentList[offset], done=0)
            else:   # 新增数据
                memo = Memo(project=plistModel, type=item, content=contentList[offset], done=0)
            for bi in branch_info:
                if str(item) == '7':
                    bi.if_jockjs = 1
                if str(item) == '8': 
                    bi.if_pages = 1
                if str(item) == '13':
                    bi.desc = contentList[offset]
                bi.save()
            memo.save()

        return redirect("/project/detail/%s/" % projectId)
    else:  # 显示页面
        if not memoList:
            form = MemoForm()
        else:
            form = []
            for m in memoList:
                memo = MemoForm({'type': m.type, 'content': m.content, 'memoId': m.pk})
                form.append(memo)

        return {
            'form': form,
            'id': projectId,
            'nullform': MemoForm()
        }


def __buildQuery(query='', day='', user=None, archived=None):
    import re
    q = Project.objects.filter()

    if query:
        pmtR = r'(pmt)\s*[-－:]?\s*(\d+)?'
        hotfixR = r'(hotfix)\s*[-－:]?\s*(\d+)?'
        creatorR = r'(author)\s*[：:]?\s*(\w+)'
        statusR = r'(attr)\s*[：:]?\s*(\S+)'
        anyR = r'()(\S+)'

        match = re.match(pmtR, query, re.I) or \
                re.match(hotfixR, query, re.I) or \
                re.match(creatorR, query, re.I) or \
                re.match(statusR, query) or \
                re.match(anyR, query)

        q = {
            'pmt': lambda id: q.filter(type__exact=1, relatedId__exact=id) if id else q.filter(type__exact=1),
            'hotfix': lambda id: q.filter(type__exact=2, relatedId__exact=id) if id else q.filter(type__exact=2),
            'author': lambda name: q.filter(createPerson__exact=User.objects.filter(username__iexact=name)[0].id) if len(User.objects.filter(username__iexact=name)) > 0 else q.filter(createPerson__exact=0),
            'attr': lambda status: {
                u'待开发': (lambda: q.filter(status__exact=1))(),
                u'正在开发': (lambda: q.filter(status__exact=2))(),
                u'正在测试': (lambda: q.filter(status__exact=3))(),
                u'待合并': (lambda: q.filter(status__exact=4))(),
                u'待上线': (lambda: q.filter(status__exact=5))(),
                u'已上线': (lambda: q.filter(status__exact=6))(),
                'testing': (lambda: q.filter(testType__exact=1))(),
                'notesting': (lambda: q.filter(testType__exact=2))(),
            }[status],
            '': lambda any: q.filter(name__icontains=any)
        }[match.group(1).lower()](match.group(2)) if match else q

    if day:
        import time
        from datetime import datetime, timedelta
        now = datetime.now()
        tomorrowString = (now + timedelta(hours=24)).strftime("%Y-%m-%d")
        # next7Days = (now + timedelta(days=7)).strftime("%Y-%m-%d")
        weekOffset = int(datetime.now().strftime("%w"))
        beginOfThisWeek = (now - timedelta(days=weekOffset)).strftime("%Y-%m-%d")
        endOfThisWeek = (now + timedelta(days=(7-weekOffset))).strftime("%Y-%m-%d")

        todayString = time.strftime("%Y-%m-%d", time.localtime())

        if day == 'today':
            q = q.filter(onlineDate__exact=todayString)
        elif day == 'tomorrow':
            q = q.filter(onlineDate__exact=tomorrowString)
        elif day == 'week':
            q = q.filter(onlineDate__lte=endOfThisWeek, onlineDate__gt=beginOfThisWeek)
        if day == 'delayed':
            q = q.filter(delay='1')
        else:
            pass

    if user:
        personIds = [person.project.id for person in RelatedPerson.objects.filter(chineseName=user.first_name)]
        q = q.filter(Q(id__in=personIds) | Q(createPerson__exact=user.id))

    if archived:
        q = q.filter(archived=True)
    else:
        pass
        # q = q.filter(archived=False)

    return q


def dispatch(request):
    '''
    ajax 请求分发器
    '''
    paramDict = request.REQUEST
    requestInfo = ''
    if 'action' in paramDict:
        action = paramDict['action']

    if action == 'get_ibug_list':
        requestInfo = getIbugList(paramDict.get('user', ''))

    if action == 'get_pmt_list':
        requestInfo = getPmtList(paramDict.get('user', ''))

    if action == 'get_pmt':
        requestInfo = getPmt(paramDict.get('pmt', ''))

    if action == 'get_branch_log':
        requestInfo = get_branch_log(paramDict)

    #修改上线日期
    if(action == 'update_date'):
        responseInfo = update_date(request.REQUEST)

    #修改仓库
    if(action == 'update_remote'):
        responseInfo = update_remote(request.REQUEST)

    #分支是否废弃
    if(action == 'update_gc'):
        responseInfo = update_gc(request.REQUEST)


    #修改上线版本库
    if(action == 'update_create_version'):
        responseInfo = update_create_version(request.REQUEST)

    # 创建分支
    if action == 'create_branch':
        result, message, branch = createBranch(paramDict.get('projectId', 0))
        requestInfo = json.dumps({'result': result, 'message': message, 'data': {'branch': branch}})

    # 检查 git branch 是否存在
    if action == 'check_branch_exist':
        requestInfo = checkBranchExist(paramDict.get('branchName', ''))

    if action == 'update_status':
        requestInfo = updateStatus(paramDict.get('projectId', 0), paramDict.get('value', 0))

    # 标记测试完成
    if action == 'test_completed':
        result, message = testCompleted(paramDict.get('projectId', 0),request.user)
        requestInfo = json.dumps({'result': result, 'message': message})

    # 更新 fp 环境上的代码
    if action == 'refresh_fp':
        result, message, gitOutputs = pullRebase(paramDict)
        requestInfo = json.dumps({'result': result, 'message': message, 'outputs': gitOutputs})

    # rebase master 代码
    if action == 'rebase_master':
        result, message, gitOutputs = rebaseMaster(paramDict,request.user)
        requestInfo = json.dumps({'result': result, 'message': message, 'outputs': gitOutputs})

    # create new branch 代码
    if action == 'create_new_branch':
        requestInfo = createNewBranch(paramDict,request.user)

    # 测试环境更新到最新代码
    if action == 'refresh_pg':
        result, message, gitOutputs = refresh_pg(paramDict,request.user)
        requestInfo = json.dumps({'result': result, 'message': message, 'outputs': gitOutputs})

    # 归档项目
    if action == 'archive':
        result, message = archive(paramDict)
        requestInfo = json.dumps({'result': result, 'message': message})
    # 延期项目
    if action == 'delayed':
        result, message = delayed(paramDict)
        requestInfo = json.dumps({'result': result, 'message': message})

    # 取消归档
    if action == 'unarchive':
        result, message = unarchive(paramDict)
        requestInfo = json.dumps({'result': result, 'message': message})

    # 分支合并回来源分支
    if action == 'merge_back':
        result, message, gitOutputs = mergeBack(paramDict)
        requestInfo = json.dumps({'result': result, 'message': message, 'outputs': gitOutputs})

    # 标记为已合并
    if action == 'merged_back':
        result = mergedBack(paramDict)
        requestInfo = json.dumps({'result': result, 'message': ''})

    # 标记为已上线
    if action == 'published':
        result = published(paramDict)
        requestInfo = json.dumps({'result': result, 'message': ''})

    # 标记上线备忘为已完成
    if action == 'mark_memo_done':
        if 'memoId' in paramDict and 'done' in paramDict:
            result = MemoModule.markMemoDone(paramDict['memoId'], True if paramDict['done'] == '1' else False)
            requestInfo = json.dumps({'result': result, 'message': '', 'data': {'done': paramDict['done']}})

    return HttpResponse(requestInfo)


def getIbugList(user):
    '''
    获取 ibug 列表
    传递参数 user:xxx
    '''
    productBugs = Ibug(username=user, env=1, status=1).getDetailInfos()
    testBugs = Ibug(username=user, env=3, status=1).getDetailInfos()
    bugs = productBugs + testBugs

    if bugs:
        # 已经创建 gomboc 项目的 ibug 列表
        exists = Project.objects.filter(type=2).all()

        # 返回还没创建 gomboc 项目的 ibug
        return json.dumps([bug for bug in bugs if int(bug['id']) not in [exist.relatedId for exist in exists]])
    else:
        return json.dumps([])


def getPmtList(user):
    '''
    获取 pmt 列表
    传递参数 user:xxx
    '''
    projects = Pmt().getOriginListByUserName(user)['$myHaveTaskProjects']

    # 获取已经创建pmt项目列表
    exists = Project.objects.filter(type=1).all()
    # exists = []

    # 返回还没有创建 gomboc 项目的 pmt 项目
    return json.dumps([project for project in projects if int(project['id']) not in [exist.relatedId for exist in exists]])


def getPmt(pmt):
    project = Pmt().getProjectDetailById(pmt)
    return json.dumps(project)


def createBranch(projectId):
    '''
    创建分支
    '''
    if projectId:
        return ProjectModule.createBranch(projectId=projectId)
    else:
        return False, ''


def createNewBranch(requestInfo,user):
    '''
    创建新分支
    '''
    projectId = int(requestInfo['projectId'] or 0) if 'projectId' in requestInfo else 0
    branch = requestInfo['branch_name'] if 'branch_name' in requestInfo else ''
    branch_type = requestInfo['branch_type'] if 'branch_type' in requestInfo else ''
    nowNum=branch[-1]
    try:
        num=int(nowNum)
        num = num + 1
        index=branch.find('-',8)
        branch_start=branch[0:index]
        branch_end=branch[index:40]
        branch_end = branch_end.replace(str(nowNum), str(num))
        branch_name =branch_start+branch_end
    except:
        num=1
        branch_name = branch+str(num)
    pb = Branch.objects.get(project=projectId)
    pb.name = branch_name
    pb.save()
    pl = Project.objects.get(id=projectId)
    pl.status = 3

    pl.save();
    remote = ""
    app_info = ""
    arr_branch_old = []
    arr_branch = []
    arr_remote = []
    for app in branch_type.split(','):

        if app == "member":
            app = "anjuke"
        if "_usersite" in app and "api_usersite" != app:
            app = "anjuke_usersite"
        if app+"," not in remote:
            remote=remote+app+","
            branch_name1=branch+"-"+app
            branch_remote = BranchInfo.objects.filter(branch_name = branch_name1)[0]
            arr_branch.append(branch_name+"-"+app)
            arr_branch_old.append(branch_name1)
            arr_remote.append(branch_remote.create_version)
#    branch_remote = BranchInfo.objects.filter(plist_id = projectId)
#    for b in branch_remote:
#        b.gc = 0

#        b.create_version = ''
#        b.save()
    InsertInfo.insert(branch_name,remote,projectId,pl.status)
    for i in range(len(arr_branch)):
        print (arr_branch[i])
        print (arr_remote[i])
        print (arr_branch_old[i])
        branch_remote = BranchInfo.objects.filter(branch_name = arr_branch[i])[0]
        branch_remote.create_version = arr_remote[i]
        branch_remote.gc = 1
        branch_remote.save()
        branch_remote = BranchInfo.objects.filter(branch_name = arr_branch_old[i])[0]
        branch_remote.create_version = ''
        branch_remote.gc = 0
        branch_remote.save()
    
    Git.createNewBranch(branch_name,remote,projectId,user)
    return 'OK'

def checkBranchExist(branchName):
    '''
    检查分支信息是否存在
    '''
    #组建bash查询语句
    gitOpPath = settings.TEMP_OP_PATH
    try:
        branchList = Git.getLocalBranchList(gitOpPath)
    except ValidationError:
        return "CheckBranchExist Failure"

    if branchName in branchList:
        return 1
    else:
        return -1


def checkHasBranchRsync(requestInfo):
    '''
    判断分支是否已经部署到 dev
    '''
    if 'projectId' in requestInfo:
        projectId = requestInfo['projectId']
        branch = Branch.objects.filter(project=projectId)
        if len(branch) == 0:
            return '-1'
        else:
            branch = branch[0]
        if branch.pdevInfo == '':
            return '-1'
        else:
            return branch.pdevInfo


def updateStatus(projectId, value):
    plistItem = Project.objects.get(id=projectId)
    plistItem.setStatus(value)
    return 1



def testCompleted(projectId,user):
    return ProjectModule.testCompleted(projectId,user)


def getAvailableStaff(requestInfo):
    '''
    获取可用的员工列表
    '''
    if 'pmtId' in requestInfo:
        pmtId = requestInfo['pmtId']
        pmtInfo = Pmt()
        try:
            staffList = pmtInfo.getRelativeStaffsByProjectId(pmtId)
        except ValidationError:
            return '获取相关人员列表出现异常'

        relatedPersons = []

        #获取目前已有的员工
        if 'listId' in requestInfo:
            listId = requestInfo['listId']
            from project.models import RelatedPerson
            relatedPersons = [item.name for item in RelatedPerson.objects.filter(project=listId)]

        staffList = [item for item in staffList if item['english_name'] not in relatedPersons]
        if len(staffList) > 0:
            return json.dumps(staffList)
        else:
            return "no available staff"
    else:
        return "invalidate"


def pullRebase(requestInfo):
    '''
    更新 fp 环境代码至最新
    '''
    fpId = int(requestInfo['fpId'] or 0) if 'fpId' in requestInfo else 0

    if fpId > 0:
        fp = Fp.objects.get(pk=fpId)
        result, message, gitOutputs = Git.pullRebase(fp.path, fp.branch)
        return result, message, gitOutputs
    else:
        return False, '参数错误', []

def rebaseMaster(requestInfo,user):
    '''
    rebase master
    '''
    projectId = int(requestInfo['projectId'] or 0) if 'projectId' in requestInfo else 0
    branch_name = requestInfo['branch_name'] if 'branch_name' in requestInfo else ''
    branch_type = requestInfo['branch_type'] if 'branch_type' in requestInfo else ''
    new_remote=""
    for app in branch_type.split(','):
        if app == "member":
            app = "anjuke"
        if "_usersite" in branch_type and "api_usersite" != branch_type:
            app = "anjuke_usersite" 
        if app +"," not in new_remote:
            new_remote = new_remote + app + ","

    result,message,gitOutputs = Git.rebaseMaster(branch_name,new_remote,projectId,user)
    return result, message,gitOutputs


def refresh_pg(requestInfo,user):
    '''
    测试环境更新到最新代码
    '''
    projectId = int(requestInfo['projectId'] or 0) if 'projectId' in requestInfo else 0
    remote = requestInfo['remote'] if 'remote' in requestInfo else ''
    fpxx = requestInfo['fpxx'] if 'fpxx' in requestInfo else ''
    if projectId > 0:
        branch_name = ProjectModule.getBranchByPid(projectId)
        result,message,gitOutputs = Git.refresh_pg(branch_name,projectId,fpxx,user,remote)
        return result, message,gitOutputs
    else:
        return False, '参数错误', []

def archive(requestInfo):
    '''
    归档项目
    '''
    projectId = int(requestInfo['projectId']) if 'projectId' in requestInfo else 0

    if projectId:
        result, message = ProjectModule.archive(projectId)
        return result, message
    else:
        return False, '参数错误'


def delayed(requestInfo):
    '''
    归档项目
    '''
    projectId = int(requestInfo['projectId']) if 'projectId' in requestInfo else 0

    if projectId:
        result, message = ProjectModule.delayed(projectId)
        return result, message
    else:
        return False, '参数错误'

def unarchive(requestInfo):
    '''
    取消归档项目
    '''
    projectId = int(requestInfo['projectId']) if 'projectId' in requestInfo else 0

    if projectId:
        result, message = ProjectModule.unarchive(projectId)
        return result, message
    else:
        return False, '参数错误'


def mergeBack(requestInfo):
    '''
    分支合并入回来源分支
    '''
    projectId = int(requestInfo['projectId']) if 'projectId' in requestInfo else 0
    project = Project.objects.get(id=projectId) if projectId > 0 else None

    if project:
        result, message, gitOutputs = Git.mergeToBranch(project.branch, project.parent.branch if project.parent else project.branch)

        if result:
            project.setStatus(5)

        return result, message, gitOutputs
    else:
        return False, '参数错误', gitOutputs


def mergedBack(requestInfo):
    '''
    分支已经合并入回来源分支，标记状态
    '''
    projectId = int(requestInfo['projectId']) if 'projectId' in requestInfo else 0
    project = Project.objects.get(id=projectId) if projectId > 0 else None

    if project:
        project.setStatus(5)

        return True
    else:
        return False


def published(requestInfo):
    '''
    该项目已上线
    '''
    import os
    projectId = int(requestInfo['projectId'] or 0) if 'projectId' in requestInfo else 0
    project = Project.objects.get(id=projectId)
    branch_name = requestInfo['branch_name'] if 'branch_name' in requestInfo else ''
    if project:
        # 同步 pmt 中的上线时间
        # TODO refine
        if project.type == 1:
            pmt = json.loads(getPmt(project.relatedId))
#            if pmt:
#                project.onlineDate = pmt['date_release']
#                project.save()
        shellPath = settings.SHELL_PATH
        os.chdir(shellPath)
        os.popen(shellPath+"remote-delete-pg.sh %s" % branch_name)
        project.setStatus(6)

        return True
    else:
        return False 


def get_branch_log(requestInfo):
#    type = requestInfo['type']
    shell = "ssh pg20-001 tail -n"+requestInfo['limit']+" /var/log/user.log |grep -nH "+requestInfo['branch_name'] 
    fp = os.popen(shell)
    infos = fp.readlines()
    infos = '\n'.join(infos)
    return infos 


def update_date(requestInfo):
    online_date = requestInfo['date']
    project_id = requestInfo['project_id']
    p = Project.objects.get(id = project_id )
    p.onlineDate = online_date
    p.save()
    branch_info = BranchInfo.objects.filter(plist_id = p.id)
    for bi in branch_info:
        bi.online_date = online_date
        bi.save()

#发布版本仓库
def update_create_version(requestInfo):
    remote = requestInfo['remote']+","
    branch_name = requestInfo['branch_name']
    branch_info = BranchInfo.objects.filter(branch_name=branch_name)[0]
    b_remote = branch_info.create_version
    branch_info.create_version = remote
    branch_info.save()
    start = branch_name.find("-")
    end = start+6
    branch_id = branch_name[start+1:end]
    project = Project.objects.filter(relatedId = branch_id).order_by('-id')[0]
    p_remote = project.remote
    else_remote = ""
    for r in p_remote.split(","):
        if r != " " and r+"," not in remote:
            else_remote += r +","
    for b in b_remote.split(","):
        if b not in remote:
            else_remote = else_remote.replace(b+",","")
    project.remote = else_remote+remote
    project.save()
       


#是否废弃
def update_gc(requestInfo):
    branch_name = requestInfo['branch_name']
    gc = requestInfo['gc']
    branch_info = BranchInfo.objects.filter(branch_name=branch_name)[0]
    all_remote = branch_info.create_version
    remote = branch_name[branch_name.rindex("-")+1:len(branch_name)] 
    branch_info.gc=gc
    branch_info.save()
    start = branch_name.find("-")
    end = start+6
    branch_id = branch_name[start+1:end]
    project = Project.objects.filter(relatedId = branch_id).order_by('-id')[0]
    p_remote = project.remote
    if gc == "1":
        branch_info.create_version = all_remote + remote + ","
        project.remote = p_remote + remote + ","
        project.save()
    else:
        branch_info.create_version = ""
        project.remote = p_remote.replace(all_remote,"") 
    project.save()
    branch_info.save()
      

def delay_project(request):     
    from django.db import connection
    f=request.GET.get('from')
    t=request.GET.get('to')
    resl= []
    cursor = connection.cursor()
    if f>1 and t>1:
        cursor.execute("select a.prelatedId,a.pdepartment,UNIX_TIMESTAMP(b.onlineDate),b.delayDate,b.person,b.delayReason,a.pname from project_plist as a,delay_info  as b where a.delay=1 and b.plist_id = a.id and UNIX_TIMESTAMP(b.onlineDate) >="+f+" and UNIX_TIMESTAMP(b.onlineDate) <="+t)
    elif f>1:
        cursor.execute("select a.prelatedId,a.pdepartment,UNIX_TIMESTAMP(b.onlineDate),b.delayDate,b.person,b.delayReason,a.pname from project_plist as a,delay_info  as b where a.delay=1 and b.plist_id = a.id and UNIX_TIMESTAMP(b.onlineDate) >="+f)
    elif t>1:
        cursor.execute("select a.prelatedId,a.pdepartment,UNIX_TIMESTAMP(b.onlineDate),b.delayDate,b.person,b.delayReason,a.pname from project_plist as a,delay_info  as b where a.delay=1 and b.plist_id = a.id and UNIX_TIMESTAMP(b.onlineDate) <="+t)
    else:
        cursor.execute("select a.prelatedId,a.pdepartment,UNIX_TIMESTAMP(b.onlineDate),b.delayDate,b.person,b.delayReason,a.pname from project_plist as a,delay_info  as b where a.delay=1 and b.plist_id = a.id")
    rs = cursor.fetchall()
    for row in rs:
        result = {}
        result = {'pmt_id':row[0],'type':row[1],'onlineDate':row[2],'delayDate':row[3],'person':'['+row[4]+']','delayReason':row[5],'title':row[6]}
        resl.append(result)
    return HttpResponse(json.dumps(resl,ensure_ascii=False))           
        
#    jsonString = []
#    id = request.GET.get('id')
#    if id >0:
#        list = Project.objects.filter(delay=1,relatedId=id)
#    else:
#        list = Project.objects.filter(delay=1)
#    for l in list:
#        result = {}
#        result={'id':l.relatedId,'name':l.name}  
#        jsonString.append(result)
#    return HttpResponse(json.dumps(jsonString))           

