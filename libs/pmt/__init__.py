#encoding=utf-8
import json,os,urllib
from django.core.exceptions import ValidationError
class Pmt:
    def __init__(self):
        self.requestUrl = "http://p.corp.anjuke.com/api/anjukeinc/projectinfo/"
        pass

    '''
    获取原始数据，形如：
    return array(
'myHaveTaskProjects'=>array('0'=>object{'id'=>8017,'summary'=>'项目名称','date_release'=>'2012-05-01','stage'=>'当前阶段'}),
'myReportedProjects'=>array('0'=>object{'id'=>8017,'summary'=>'项目名称','date_release'=>'2012-05-01','stage'=>'当前阶段'}),
'myOwnedProjects'=>array('0'=>object{'id'=>8017,'summary'=>'项目名称','date_release'=>'2012-05-01','stage'=>'当前阶段'}),
'myCcProject'=>array('0'=>object{'id'=>8017,'summary'=>'项目名称','date_release'=>'2012-05-01','stage'=>'当前阶段'}),
)
    '''
    def getOriginListByUserName(self,username):
        if username.strip() == '':
            raise ValidationError("username is not exist")
        requestUrl = self.requestUrl + "projectsbyuser/%s" %(username)
        curlHandle = urllib.urlopen(requestUrl)
        result = curlHandle.readline()
        if result.strip() != '':
			a = json.dumps(result)
			b = json.loads(a,encoding='UTF-8')
			c = b.encode('gbk','ignore')
			c = json.loads(c)
			return c
            #return json.loads(result)
        else:
            return {}

    '''获取员工有task的任务
    '''
    def getHaveTaskProjects(self,username):
        projectsInfo = self.getOriginListByUserName(username)
        if projectsInfo.has_key("$myHaveTaskProjects"):
            return projectsInfo['$myHaveTaskProjects']
        else:
            raise ValidationError("have no $myHaveTaskProjects")

    '''获取我提交的项目
    '''
    def getReportedProjects(self,username):
        projectsInfo = self.getOriginListByUserName(username)
        if projectsInfo.has_key("$myReportedProjects"):
            return projectsInfo['$myReportedProjects']
        else:
            raise ValidationError("have no $myReportedProjects")


    '''获取我负责的项目
    '''
    def getOwnedProjects(self,username):
        projectsInfo = self.getOriginListByUserName(username)
        if projectsInfo.has_key("$myOwnedProjects"):
            return projectsInfo['$myOwnedProjects']
        else:
            raise ValidationError("have no $myOwnedProjects")

    '''获取抄送给我的项目
    '''
    def getCcProjects(self,username):
        projectsInfo = self.getOriginListByUserName(username)
        if projectsInfo.has_key("$myCcProject"):
            return projectsInfo['$myCcProject']
        else:
            raise ValidationError("have no $myCcProject")

    '''通过项目ID获取项目详细信息
    '''
    def getProjectDetailById(self,projectId):
        if int(projectId) == 0:
            raise ValidationError("projectId is invalidate. projectId:"+str(projectId))

        requestUrl = self.requestUrl + "projectinfobypid/%s" %(projectId)
        curlHandle = urllib.urlopen(requestUrl)
        result = curlHandle.readline()
        if result.strip() != '':
            return json.loads(result)
        else:
            return {}

    '''通过项目号获取任务信息
    '''
    def getTaskInfoByProjectId(self,projectId):
        if int(projectId) == 0:
            raise ValidationError("projectId is invalidate. projectId:"+str(projectId))

        requestUrl = self.requestUrl + "tasksbypid/%s" %(projectId)
        curlHandle = urllib.urlopen(requestUrl)
        result = curlHandle.readline()
        if result.strip() != '':
            return json.loads(result)
        else:
            return {}

    '''通过项目号获取相关人员
    '''
    def getRelativeStaffsByProjectId(self,projectId):
        if int(projectId) == 0:
            raise ValidationError("projectId is invalidate. projectId:"+str(projectId))

        requestUrl = self.requestUrl + "staffsbypid/%s?detail=true" %(projectId)
        curlHandle = urllib.urlopen(requestUrl)
        result = curlHandle.readline().strip()

        return json.loads(result) if result != '' else {}
