#encoding=utf-8
'''
处理dev环境各种git操作
可以考虑替换为一个现成的更成熟的实现
@author: lenye01
'''

import os
import md5
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from ipBan.models import *

def getDiffOfMaster(fpPath, branchName):
    '''
    获取指定测试分支与生产环境master的区别
    '''
    if fpPath != '' and fpPath is not None:
        os.chdir(fpPath)
        os.popen("git pull  --rebase git-branch " + branchName + " && git checkout master && git pull --rebase")
        handle = os.popen("git diff master " + branchName + " --stat")
        return handle.readlines()
    return []


'''
    录入shell脚本产生的log日志
    @type 类型
    @pmt pmt关联id
    @content 内容
    '''
def insertShellLog(type=1,pmt=0,content='',operator=''):
    import time
    print content
    if pmt>0 and content!="":
        Log(type=type,
                pmt=pmt,
                content="",
                operator = operator,
                created=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ).save()
        return True
    else :
        return False,"参数不全"

def createBranch(branchName, parent='master',projectId=0,remote=""):
    '''
    创建分支
    '''
#    gitOpPath = settings.TEMP_OP_PATH
#    for appType in ("anjuke","haozu","jinpu","wechat"):
#        if isDirty(gitOpPath+appType):
#            return False, ['git 工作目录状态错误，请处理之后重试']
    '''
    调用shell脚本创建 edit 20130722 by kyou
    '''
    shellPath = settings.SHELL_PATH
    os.chdir(shellPath)
    print (branchName)
    print (remote)

    opResult = os.popen(shellPath+"create-branch.sh %s %s" % (branchName,remote))
    outputs = "<br />".join(opResult.readlines())
    #insert log
    insertShellLog(5,projectId,outputs)

    return True, outputs
    #/////////////////////////
    # PS:下面这些都不用了,你可以删掉
    #/////////////////////////

    # TODO git remote 名等移入 settings.py
    origin, gitBranch = 'origin' if parent == 'master' else 'git-branch', 'git-branch'

    commands = [
        "git fetch %s %s:%s" % (origin, parent, parent),
        "git checkout %s" % parent,
        "git pull --rebase",
        "git checkout -b %s" % branchName,
        # dev mock
        "git push %s %s:%s" % (gitBranch, branchName, branchName),
        "git checkout master"
    ]

    try:
        gitOutputs = executeCommands(gitOpPath, commands)
    except ValidationError:
        return False, gitOutputs

    return True, gitOutputs

def createNewBranch(branchName,remote="",projectId=0,user=0):
    '''
    创建分支
    '''
    shellPath = settings.SHELL_PATH
    os.chdir(shellPath)
    opResult = os.popen(shellPath+"create-branch.sh %s %s" % (branchName,remote))
    outputs_ = "<br />".join(opResult.readlines())
    #insert log
    insertShellLog(11,projectId,outputs_,user.first_name)
    return 'ok'

def test_completed(projectId,user):
    shellPath = settings.SHELL_PATH
    opResult = os.popen(shellPath+"test.sh")
    outputs_ = "<br />".join(opResult.readlines())
    try:
        insertShellLog(2,projectId,outputs_,user.first_name)
    except:
        ansertShellLog(2,projectId,outputs_,'nologin')


def branchDiff(branch_name,branch_type):
    shellPath = settings.SHELL_PATH
    os.chdir(shellPath)
    opResultlogs = ''
    outputs_ = ''
    opResult = os.popen(shellPath+"branch-diff.sh %s %s" % (branch_name,branch_type))
    outputs_ = "<br />".join(opResult.readlines())
    opResultlogs += outputs_
    #匹配是否有冲突
    preg = outputs_.find("have conflict")
    be = outputs_.find("exist")
    rst = outputs_.find("wait")
    big = outputs_.find("big")
    nochange = outputs_.find("nochange")
    errorSyntax = outputs_.find("Syntax Error")
    error_repo = outputs_.find("repo is error")
    if rst >=0:
        return '有其他项目正在操作，请稍等 ',outputs_
    elif big >=0:
        return branch_name+"-"+branch_type+' 分支修改文件太多，无法查看!',outputs_
    elif nochange >=0:
        return branch_name+"-"+branch_type+'代码未做变更! ',outputs_
    elif errorSyntax>=0:
        type = branch_type.split(',')
        b = ''
        for t in type:
            if t != "": 
                if outputs_.find("Syntax Error")>=0 :
                    branch_name1=branch_name+"-"+t
                    b=b+branch_name1+' '
        return str(b)+' PHP语法错误!',outputs_
    elif be >=0:
        type = branch_type.split(',')
        b = ''
        for t in type:
            if t != "":
                if outputs_.find("exist")>=0 :
                    branch_name1=branch_name+"-"+t
                    b=b+branch_name1+' '
        return str(b)+'分支不存在，请确认。',outputs_
    elif preg >=0:
        type = branch_type.split(',')
        b = ''
        for t in type:
            if t != "":
                if outputs_.find("have conflict "+t+"!")>=0 :
                    branch_name1=branch_name+"-"+t
                    b=b+branch_name1+' '
        message = "rebase master 出现冲突，请解决冲突,分支号为："+str(b)
        return message,outputs_
    elif error_repo >=0:
        type = branch_type.split(',')
        b = ''
        for t in type:
            if t != "":
                if outputs_.find(t+" repo is error")>=0 :
                    t1=t
                    b=b+t1+' '
        return str(b)+'仓库异常，请联系管理员 ',outputs_
    else:
        return branch_name+"-"+branch_type+' diff 成功!',outputs_


def rebaseMaster(branch_name,branch_type,projectId,user):
    shellPath = settings.SHELL_PATH
    os.chdir(shellPath)
    opResultlogs = ''
    outputs_ = ''
    opResult = os.popen(shellPath+"git-rebase-master.sh %s %s" % (branch_name,branch_type))
    outputs_ = "<br />".join(opResult.readlines())
    opResultlogs += outputs_
    #匹配是否有冲突
    preg = outputs_.find("have conflict")
    rst = outputs_.find("wait")
    error_repo = outputs_.find("repo is error")
    if rst >=0:
        return True,'有其他项目正在rebase，请稍等 ',[]
    elif error_repo >=0:
        type = branch_type.split(',')
        b = ''
        for t in type:
            if t != "":
                if outputs_.find(t+" repo is error")>=0 :
                    t1=t
                    b=b+t1+' '
        return True,str(b)+'仓库异常，请联系管理员 ',[]
    elif preg >=0:
        type = branch_type.split(',')
        b = ''
        for t in type:
            if t != "":
                if outputs_.find("have conflict "+t+"!")>=0 :
                    branch_name1=branch_name+"-"+t
                    b=b+branch_name1+' '
        message = "rebase master 出现冲突，请解决冲突,分支号为："+str(b)
        return True,message,[]
    #insert log 日志
    else:
        try:
            insertShellLog(4,projectId,outputs_,user.first_name)
        except:
            insertShellLog(4,projectId,outputs_,'noligin')
        return True,'rebase master 成功',[]

# 测试环境更新到最新代码
def refresh_pg(branchName,projectId,fpxx,user,remote):
    shellPath = settings.SHELL_PATH
    os.chdir(shellPath)
    opResult = os.popen(shellPath+"remote-refresh-pg.sh %s %s %s" % (branchName,remote,fpxx))
    outputs = "<br/>".join(opResult.readlines()) # log日志
    errorSyntax = outputs.find("Syntax Error")
    #insert log 日志
    if errorSyntax>=0:
        return False,str(outputs),[]
    else:
        try:
            insertShellLog(3,projectId,outputs,user.first_name)
        except:
            insertShellLog(3,projectId,outputs,'nologin')
        return True,'更新代码成功',[]


def mergeToBranch(branchName,branchType,branchDesc):
    '''
    把分支合并进 master
    '''
    shellPath = settings.SHELL_PATH
    os.chdir(shellPath)
    try:
        if_merge = VersionList.objects.filter(branch_name = branchName)[0]
        message = "该分支已被合并到master了，请去进行中项目里生成新分支"
    except:
        if_merge = 'no_merge'
        opResult = os.popen(shellPath+"git-merge-branch.sh %s %s %s %s" % (branchName,branchType,branchType,branchDesc))
        outputs = "<br/>".join(opResult.readlines()) # log日志
        preg = outputs.find('have conflict')
        no_branch = outputs.find('no this branch')
        error_repo = outputs.find('repo is error')
        if_push_ok = outputs.find('FAIL')
        if_pass = outputs.find('PASS')
        if error_repo >=0:
            message = str(branchType)+"仓库异常，请联系管理员"
        elif no_branch >=0:
            message = "该分支不存在，请仔细核对，专心点啊=。="
        elif preg >=0:
            message = "rebase master 出现冲突，请解决冲突,分支号为："+str(branchName)
        elif if_push_ok >=0:
            message = "git上没有显示该分支的merge信息，也没有冲突，请确认分支名"
        elif if_pass >=0:
            message = "合并成功"
        else:
            message = "no status"

    return  message

def mergeToBranchbak(branch, targetBranch='master',gitOpPath=None):
    '''
    把分支合并进 master
    现在合并 PMT 和 Hotfix 流程一样，都使用这个方法

    合并结果类似如下
    *   commit 31eeb1e91264c9a1fa6fcd6095aa3bb0e95f64f8
    |\  Merge: f1bc57f b2dcc29
    | | Author: app10-069 <app10-069@aifang.com>
    | | Date:   Thu Sep 27 11:35:00 2012 +0800
    | |
    | |     Merging Hotfix hotfix-prop2 To Master
    | |
    | * commit b2dcc29da2c8cdd50a4b710d331775600b7f73af
    | | Author: 朱建华 <alan@aifang.com>
    | | Date:   Thu Sep 27 11:30:54 2012 +0800
    | |
    | |     房源名称过滤
    | |
    | * commit 70b4720271440b2bd02d17c1ba1f0f7936e4171a
    | | Author: 朱建华 <alan@aifang.com>
    | | Date:   Thu Sep 27 11:05:10 2012 +0800
    | |
    | |     detail
    | |
    | * commit 84ebc1225474bb037c4fd904e0ae0bc3a7357084
    |/  Author: 曹宏浪 <andycao@anjuke.com>
    |   Date:   Thu Sep 27 11:07:09 2012 +0800
    |
    |       replace word
    |
    *   commit f1bc57f3f33089071d9fa151b95a2ff4b35e1053

    '''
    if  gitOpPath is None:#path 太多了,待删除
        return False,'未设置git代码仓库', []

    # TODO git remote 名等移入 settings.py
    origin, gitBranch = settings.MASTER_ALIAS if targetBranch == 'master' else settings.BRANCH_ALIAS, settings.BRANCH_ALIAS

    if isDirty(gitOpPath):
        return False, 'git 工作目录状态错误，请处理之后重试', []

    rebaseCommands = [
        "git fetch %s %s:%s" % (gitBranch, branch, branch),
        "git checkout %s" % targetBranch,
        "git pull --rebase %s %s" % (origin, targetBranch),
        "git checkout %s" % branch,
        "git pull --rebase %s %s" % (gitBranch, branch),
        "git rebase %s" % targetBranch,
    ]
    mergeCommands = [
        "git checkout %s" % targetBranch,
        "git merge --no-ff %s -m 'Merging Branch %s To %s'" % (branch, branch, targetBranch),
        # mock
        "git push %s %s:%s" % (origin, targetBranch, targetBranch),
    ]

    rebaseOutputs = executeCommands(gitOpPath, rebaseCommands)
    conflicts = [line for line in rebaseOutputs if 'CONFLICT' in line]

    # TODO executeCommands 取不到错误

    if len(conflicts) > 0:
        executeCommands(gitOpPath, ["git rebase --abort"])
        return False, 'git rebase master 冲突，请手动处理之后重试', rebaseOutputs

    mergeOutputs = executeCommands(gitOpPath, mergeCommands)

    return True, '合并成功', mergeOutputs


    gitOutputs = executeCommands(fpPath, commands)

    return True, '成功', gitOutputs

def executeCommand(fpPath, command):
    '''
    执行git命令
    '''
    if fpPath != '' and fpPath is not None:
        #新建锁 锁命名方式 md5(fpPath).lock
        LockName = "/tmp/" + md5.new(fpPath).hexdigest() + ".lock"

        if os.path.isfile(LockName):
            raise ValidationError(fpPath + " is locking,you can delete lock file or wait for a moment")
        else:
            open(LockName, 'w').close()
            os.chdir(fpPath)
            try:
                handle = os.popen(command)
            except ValidationError:  # 出现异常，如果锁文件存在，删除锁
                if os.path.isfile(LockName):
                    os.remove(LockName)

            if os.path.isfile(LockName):
                os.remove(LockName)
            return handle.readlines()
    return []

def executeCommands(fpPath, commands, exceptionExit=False):
    '''
    执行一连串命令
    fpPath 文件路径
    commands 命令列表
    exceptionExit 异常退出，如果为真，遇到异常直接退出，并返回－1
    '''

    result = []
    if type(commands) == list and len(commands) > 0:
        for command in commands:
            print command
            # print isDirty(fpPath)
            if exceptionExit and isDirty(fpPath):
                raise ValidationError("Commands Execute Failure!")
            result.extend(executeCommand(fpPath, command))
    return result


def getDiffBetweenBranchAndMaster(fpPath, branchName):
    '''
    获取指定分支与master的区别
    是getDiffOfMaster的优化版
    '''
    command = "git checkout master && git pull --rebase && git fetch git-branch \
    " + branchName + ":" + branchName + "&& git checkout " + branchName
    executeCommand(fpPath, command)
    return executeCommand(fpPath, "git diff master")


def isDirty(fpPath):
    '''
    检查分支状况，如果分支为不干净分支，返回True, 否则，返回False
    '''
    #如果有未跟踪的文件，返回True 涵盖修改文件，rebase需要手动合并的状态
    if untrackedFiles(fpPath):
        return True
    return False


def untrackedFiles(fpPath):
    '''
    获取未跟踪的文件 untracked
    '''
    if os.path.isdir(fpPath) and os.path.isdir(fpPath + "/.git"):
        os.chdir(fpPath)
        return execute("git status --untracked-files=no -s")
    else:
        raise ValidationError("path is not exist or dirctory is not a git repo")


def execute(command):
    '''
    shell命令执行 调用popen命令
    '''
    if str(command) != '':
        handle = os.popen(command)
        return handle.readlines()
    else:
        raise ValidationError("command should not be empty")


def getLocalBranchList(fpPath):
    '''
    获取本地分支
    '''
    command = "git branch -l"
    branchList = executeCommand(fpPath, command)
    if len(branchList) > 0:
        branchList = [item.strip(' *\n') for item in branchList]
        return branchList
    return []


def getRemoteBranchList(fpPath, alias):
    '''
    获取远程分支
    '''
    if alias in getRemoteAlias(fpPath):
        command = "git fetch " + alias
        executeCommand(fpPath, command)
        command = "git branch -r"
        branchList = executeCommand(fpPath, command)
        if len(branchList) > 0:
            branchList = [[i.strip(" \n") for i in item.split('/')] for item in branchList]
            newList = []
            for item in branchList:
                if item[0] == alias:
                    newList.append(item[1])
            return newList
        return []
    else:
        raise ValidationError(alias + " is not exist. throw this exception in getRemoteBranchList")


def getRemoteAlias(fpPath):
    '''
    获取alias
    '''
    command = "git remote -v"
    aliasList = executeCommand(fpPath, command)
    if len(aliasList) > 0:
        return list(set([item.split("\t")[0] for item in aliasList]))
    else:
        return []


def isBranchExist(fpPath, branchName, isRemote=False):
    '''
    检查分支是否存在
    isRemote 如果为True，检查远程分支是否存在 默认为False
    '''
    if isRemote:
        pass
    else:
        #branchList = executeCommand()
        pass
