#encoding=utf-8
'''
项目业务逻辑
'''

from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from libs.util import pager
from libs.git import Git
from libs.ibug import Ibug
from libs.pmt import Pmt
from project.models import Project, ProjectExtend, Branch, ProjectTime, RelatedPerson, Memo,\
    Design, Cate, ProjectCate, DesignAttach , DelayInfo
from webgit.models import Fp
from webgit.models import Log
from deploy.models import BranchInfo
import time
import os
from libs.util.uploadHandler import upload
import random
import string

class ProjectModule:

    '''
    录入shell脚本产生的log日志
    @type 类型
    @pmt pmt关联id
    @content 内容
    '''
    @staticmethod
    def insertShellLog(type=1,pmt=0,content='',operator=0):
        if pmt>0 and content!="":
            Log(type=type,
                pmt=pmt,
                content=content,
                operator = 222,
                created=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            ).save()
            return True
        else :
            return False,"参数不全"
    '''
    根据projectId 获得 branch分支
    '''
    @staticmethod
    def getBranchByPid(projectId):
        Pgs = Branch.objects.filter(project=projectId)
        pg = Pgs[0] if len(Pgs) > 0 else None
        branch = pg.name if pg else ''
        return branch

    '''
    获取项目详情
    '''
    @staticmethod
    def getProject(projectId):
        project = Project.objects.get(id=projectId)
        projectExtend = ProjectExtend.objects.filter(project=project)
        projectBranch = Branch.objects.filter(project=projectId)
        creator = User.objects.get(id=project.createPerson)

        # 如果 project 类型是 pmt，获取该 pmt 未处理的 bug
        bugs = Ibug(pmt=project.relatedId, env=2, status=0).getDetailInfos() or [] if project.type == 1 else []

        # 相关员工信息
        persons = RelatedPerson.objects.filter(project=project) if project.type == 1 else []

        # 获得 git log 日志
        gitrs = Log.objects.filter(pmt=projectId)

        listgitrs = []
        if len(gitrs)>0:
            for listItem in gitrs:
                listItem.typestr = Log.TYPES[listItem.type]
                listgitrs.append(listItem)

        listgitrslog = listgitrs if len(listgitrs)>0 else []

        # 查看当前分支与线上 master 的 diff 信息
        # 获取分支信息
        # branches = Branch.objects.filter(project=project)
        # diff = Git.getDiffBetweenBranchAndMaster(settings.TEMP_OP_PATH, branches[0].name) if len(branches) > 0 else []

        fps = Fp.objects.filter(branch=project.branch)
        fp = fps[0] if len(fps) > 0 else None
#        project.branch_name = projectBranch.name
        try:
            project.branch_name = projectBranch[0].name
        except:
            project.branch_name = project.branch
        project.gitlogs = listgitrslog
        project.fp = fp
        project.description = projectExtend[0].description if len(projectExtend) > 0 else ''
        project.creator = creator
        project.bugs = bugs
        project.relatedPersons = persons
        project.diff = []
        project.memos = MemoModule.getMemos(project)
        project.subprojects = Project.objects.filter(parent=project)
        project.real_branch_name = BranchInfo.objects.filter(plist_id = projectId) 
        project.delay_info = DelayInfo.objects.filter(plist_id = projectId)
        try:
            project.design = Design.objects.get(project=project)
        except Design.DoesNotExist:
            project.design = None

        return project

    '''
    获取项目列表
    '''
    @staticmethod
    def getProjects(q=None, page=1, size=10):
        q = Project.objects.filter() if q == None else q
        projects = q.order_by('-id')

        paginator = Paginator(projects, size)

        try:
            page = int(page)
        except ValueError:
            page = 1

        try:
            projects = paginator.page(page)
            for p in projects:
                p.creator = User.objects.get(id=p.createPerson)

        except (EmptyPage, InvalidPage):
            projects = paginator.page(paginator.num_pages)

        paged = pager.Pager(paginator.page_range, page).getRange()

        return projects, paged

    '''
    创建项目
    '''
    @staticmethod
    def create(data, user):
        createDate = datetime.now().strftime('%Y%m%d')
        projectsToday = Project.objects.filter(createDate=createDate).order_by('-id')
        nextIndex = "%02d" % (1 + int(projectsToday[0].dateIndex) if projectsToday.count() else 1)

        parent = Project.objects.get(id=data['parent']) if data['parent'] != '0' else None

        project = Project(status=1, name=data['name'], type=data['type'], department=data['department'],suffix=data['suffix'],remote=data['allRemote'],
            relatedId=data['relatedId'], onlineDate=data['onlineDate'],
            testType=1, createDate=createDate, dateIndex=nextIndex,
            createPerson=user.pk, parent=parent, pmtType=data['pmtType'],delay=0)

        # 新建项目
        project.save()
        projectExtend = ProjectExtend(project=project, description=data['description'])
        projectExtend.save()

        try:
            staffs = Pmt().getRelativeStaffsByProjectId(project.relatedId)['task'] or []
            print ("---------------")
            print (staffs)
#            if len(staffs) > 0:
            for staff in staffs:
                position=staff['position']
                if '质量' in position:
                    position='QA'
                staffModel = RelatedPerson(project=project, relatedId=1, \
                    name=staff['english_name'], chineseName=staff['chinese_name'], \
                    email=staff['email'], position=position, type=0)
                staffModel.save()
        except:
            print("==========")

        return project.id

    @staticmethod
    def updateInfo(projectId,relatedId):
        project = Project.objects.get(pk=projectId)
        info = RelatedPerson.objects.filter(project=projectId)
        for i in info:
            i.delete()
        try:
            staffs = Pmt().getRelativeStaffsByProjectId(project.relatedId)['task'] or []
            print ("---------------")
            print (staffs)
            for staff in staffs:
                position=staff['position']
                if '质量' in position:
                    position='QA'
                staffModel = RelatedPerson(project=project, relatedId=1, \
                    name=staff['english_name'], chineseName=staff['chinese_name'], \
                    email=staff['email'], position=position, type=0)
                staffModel.save()
        except:
            print("==========")

    '''
    获取项目的进入各阶段的时间
    '''
    @staticmethod
    def getProjectTimes(projectId):
        times = ProjectTime.objects.filter(project=projectId) if projectId else None
        return times

    @staticmethod
    def delayed(projectId):
        project = Project.objects.get(pk=projectId)
        project.delay = 1
        project.save()
        return True, ''

    @staticmethod
    def archive(projectId):
        project = Project.objects.get(pk=projectId)
        project.archived = True
        project.save()
        return True, ''

    @staticmethod
    def unarchive(projectId):
        project = Project.objects.get(pk=projectId)
        project.archived = False
        project.save()
        return True, ''

    '''
    创建项目的分支
    '''
    @staticmethod
    def createBranch(projectId):
        project = Project.objects.get(pk=projectId) if projectId else None
        if not project:
            return False, ''

        # 临时操作仓库目录 todo
        gitOpPath = settings.TEMP_OP_PATH
        #~ 判断分支是否已经创建
        createdFlag = True
        for appType in ("anjuke","haozu","jinpu"):
            try:
                branches = Git.getRemoteBranchList(gitOpPath+appType, settings.BRANCH_ALIAS)
            except ValidationError:
                return False, "get Remote Branch List Failure", project.branch
            realBranch = project.branch+"-"+appType
            if realBranch not in branches:
                createdFlag = False
                break

        if createdFlag :
            # 将项目状态更改为正在开发
            project.setStatus(2)
            return False, "Have Created", project.branch
        else:
            result, messages = Git.createBranch(project.branch, project.parent.branch if project.parent else 'master',projectId,project.remote)

            if not result:
                return False, messages, ''

            Branch(name=project.branch,
                    pcreateDateTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    status=1,
                    project=project
            ).save()

            InsertInfo.insert(project.branch,project.remote,project.id,project.status);
            # 将项目状态更改为正在开发
            project.setStatus(2)

            return True, "Created Successfully!", project.branch


    @staticmethod
    def testCompleted(projectId,user):
        project = Project.objects.get(id=projectId)
        subprojects = Project.objects.filter(parent=project)

        unmergedSubprojects = [subproject for subproject in subprojects if subproject.status < 5]
        hasOpenBugsSubprojects = [subproject for subproject in subprojects if ProjectModule.hasOpenBugs(subproject.id)]

        if ProjectModule.hasOpenBugs(projectId):
            return False, '仍有 Bug 未关闭'
        elif len(unmergedSubprojects) > 0:
            return False, '仍有子项目未合并'
        elif len(hasOpenBugsSubprojects) > 0:
            return False, '子项目仍有 Bug 未关闭'
        else:
            project.setStatus(4)
            branch_info = BranchInfo.objects.filter(plist_id=project.id,status__lte=4)
            for bi in branch_info:
                bi.status=4
                bi.save()
            print (user) 
            Git.test_completed(projectId,user)
            return True, ''

    @staticmethod
    def hasOpenBugs(projectId):
        project = Project.objects.get(id=projectId)
        bugs = Ibug(pmt=project.relatedId, env=2, status=0).getDetailInfos() or [] if project.type == 1 else []

        return len([bug for bug in bugs if bug['closed_at'] == None]) > 0


class MemoModule:

    # def createMemo():

    # def modifyMemo():

    '''
    标记 memo 已完成
    '''
    @staticmethod
    def markMemoDone(memoId, done=True):
        memo = Memo.objects.get(pk=memoId)
        if memo:
            memo.done = 1 if done else 0
            memo.save()
            return True
        else:
            return False

    '''
    获取项目的所有 memo
    '''
    @staticmethod
    def getMemos(project):
        memos = Memo.objects.filter(project=project)
        if memos:
            for memo in memos:
                if Memo.MEMO_TYPE[memo.type - 1]:
                    memo.type = Memo.MEMO_TYPE[memo.type - 1][1]

        return memos


class cateModule:

    '''
    根据cateid获取子类
    '''
    def getCateByParentId(self,parentId):
        if parentId == None:
            return None
        children = Cate.objects.filter(parentId=parentId,status=0)
        return children
    '''
    插入关系
    '''
    def replaceProjectCate(self,pid,catelist,operator):
        try:
            project = Project.objects.get(pk=pid)
        except Project.DoesNotExist :
            return None

        #TODO 优化 只修改被删的状态
        try:
            ProjectCate.objects.filter(plist=project).update(status=1)
        except ProjectCate.DoesNotExist :
            pass

        for cid in catelist:
            now = time.strftime("%Y-%m-%d %X", time.localtime())

            cate = Cate.objects.get(pk=cid)
            try:#更新
                model = ProjectCate.objects.get(plist=project,cate=cate)
                model.status = 0
            except ProjectCate.DoesNotExist :#插入
                model = ProjectCate(plist=project,cate=cate,creater=operator,created=now,status=0)

            model.save()

        return

    '''
    获取项目的功能块
    '''
    def getCateListByProjectId(self,pid,showlink=True):
        try:
            project = Project.objects.get(pk=pid)
        except Project.DoesNotExist :
            return None
        #
        pc_list = ProjectCate.objects.filter(plist=project,status=0)
        if not pc_list:
            return None

        cateList = []
        for pc in pc_list:
            #获取cate id
            cate = pc.cate_id
            cateList.append(cateModule.getParentNodeById(cate))

        ul_str = "<ul class='select_list unstyled'>"
        for row in cateList:
            link_str = ''
            if showlink:
                link_str = "<a class='btn btn-info btn-mini' href='javascript:;'><i class='icon-minus icon-white'></i></a>"
            li_str = "<li>%s" %link_str
            #显示功能下拉框
            for cid in row[::-1]:
                #最后一个select加上name
                name_str ="name='cate'" if cid == row[0] else ''
                select_str = "<select class='cate_list span2' %s><option value='' style='color: gray'>请选择功能集</option>" %name_str
                try:
                    currCate = Cate.objects.get(pk=cid)
                except Cate.DoesNotExist :
                    return None
                brothers = Cate.objects.filter(parentId=currCate.parentId,status=0)
                for bro in brothers:
                    checked = "selected='selected'" if bro.id==cid else ''
                    opt_str = "<option %s value='%d'>%s</option>" %(checked, bro.id, bro)
                    select_str = select_str + opt_str
                select_str += "</select> "
                li_str += select_str
            li_str += "</li>"
            ul_str += li_str
        ul_str += "</ul>"
        return ul_str


    '''
    获取父类
    '''
    @staticmethod
    def getParentNodeById(id):
        result = []
        try:
            currCate = Cate.objects.get(pk=id)
        except Cate.DoesNotExist :
            return None
        result.append(currCate.id)
        pnode = cateModule.getParentNodeById(currCate.parentId)
        if pnode != None:
            result.extend(pnode)
        return result

    '''
    插入关系
    '''
    def createDesignAttach(self,pid,filelist,operator):
        try:
            project = Project.objects.get(pk=pid)
        except Project.DoesNotExist :
            return None

        url_path = settings.UPLOAD_ATTACH_URL+"/"
        #路径获取
        if('UPLOAD_PATH' in dir(settings) and 'UPLOAD_ATTACH_URL' in dir(settings)):
            path = settings.UPLOAD_PATH + url_path
        else:
            path = "~/"
        for file_tmp in filelist:
            now = time.strftime("%Y-%m-%d %X", time.localtime())

            #上传
            #获取扩展
            splite_name = os.path.splitext(file_tmp._name)
            ext = ''
            ran =  '_' + str(random.randint(1000,9999))
            if len(splite_name) > 1:
                ext = splite_name[-1]
            new_name = str(int(time.time()))+ ran + ext.lower()
            upload_res = upload(file_tmp, path, new_name, "wb+")

            if upload_res:
                model = DesignAttach(project=project,name=file_tmp._name,path=settings.STATIC_URL+url_path+new_name,status=0)
            model.save()

        return

class InsertInfo:
    @staticmethod
    def insert(branch,remote,pid,status):
        start = branch.find("-")
        end = start+6
        branch_id = branch[start+1:end]
        project = Project.objects.filter(relatedId = branch_id)[0]
        for branch_type in remote.split(','):
            branch_name=branch + "-"+ branch_type
            if branch_type != "":
                try:
                    BranchInfo(branch_name = branch_name,
                       online_date = project.onlineDate,
                       title = project.name,
                       plist_id = pid,
                       status = status,
                       if_check = 0,
                       if_jockjs = 0,
                       if_pages = 0,
                       create_version = branch_type + ",",
                       gc = 1
                    ).save()             
                except:
                    pass
