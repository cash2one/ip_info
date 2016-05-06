#encoding=utf-8
from django.db import models
from datetime import datetime


class Project(models.Model):
    '''
    项目
    '''

    STATUSES = {
        1: '待开发',
        2: '正在开发',
        3: '正在测试',
        4: '待合并',
        5: '待上线',
        6: '已上线',
    }

    TYPES = {
        1: 'pmt',
        2: 'hotfix'
    }
    DEPS = { 
        3: 'site',
        4: 'ipad',
        5: 'tw',
        6: 'api',
    } 
    class Meta:

        db_table = 'project_plist'

        # permissions = (
        #     # 创建分支
        #     ('create_branch', 'Can create a branch'),
        #     # 同步到 fp 环境
        #     ('sync_to_fp', 'Can sync a branch to a fp to test'),
        #     # 测试完成
        #     ('tested', 'Can mark a project as tested'),
        #     # 合并入 master
        #     ('merge', 'Can merge a branch to master'),
        #     # 发布到 stage 环境
        #     ('publish_to_stage', 'Can publish a project to stage'),
        #     # 发布上线
        #     ('publish', 'Can publish a project'),
        # )

    # 项目名称
    name = models.CharField(max_length=50, db_column='pname')
    #主键
    #id = models.IntegerField(primary_key=True)
    # 项目类型 1：PMT  2：Hotfix
    type = models.SmallIntegerField(max_length=2, db_column='ptype')
    # 3 site  4iPad
    department = models.SmallIntegerField(max_length=2, db_column='pdepartment')
    # 所选仓库
    remote = models.CharField(max_length=300, db_column='remote')
    # 项目相关联id 可以是pmt 也可以是ibug id
    relatedId = models.IntegerField(max_length=10, db_column='prelatedId')
    # 项目状态 1：待开发  2：正在开发  3：正在测试 4：待合并 5：待上线 6：已上线
    status = models.SmallIntegerField(max_length=2, db_column='pstatus')
    # 测试类型 1:需测试 2:无需测试
    testType = models.SmallIntegerField(max_length=2, db_column='ptestType')
    # 上线时间
    onlineDate = models.DateField(db_column='ponlineDate')
    # 创建人
    createPerson = models.CharField(max_length=20, db_column='pcreatePerson')
    # 创建时间
    createDate = models.CharField(max_length=8, db_column='createDate')
    # 创建索引（当天的序列号）
    dateIndex = models.CharField(max_length=2, db_column='dateIndex')
    # 后缀
    suffix = models.CharField(max_length=50, blank=True, db_column='psuffix')
    # 多人开发的副分支的主分支的项目id
    parent = models.ForeignKey('self', null=True, blank=True, db_column='parent_id')
    # pmt类型 1 单人开发 2 多人开发的主分支 3 多人开发的副分支
    pmtType = models.SmallIntegerField(max_length=1, default=1, db_column='pmtType')
    # 是否已归档 0 未归档, 1 已归档
    archived = models.SmallIntegerField(max_length=1, default=0, db_column='archived')
    # 延期
    delay = models.SmallIntegerField(max_length=2)

    def __getattribute__(self, name):
        '''
        计算属性
        '''
        try:
            computed_attributes = {
                'branch': lambda self: "%s-%d-%s%s" % (self.TYPES[self.type], self.relatedId, self.DEPS[self.department], self.suffix),
                'url': lambda self:
                    "http://p.corp.anjuke.com/project/detail?id=%d" % self.relatedId if self.type == 1 else
                    "http://ibug.corp.anjuke.com/ticket/detail?ticket_id=%d" % self.relatedId,
                'typeAlias': lambda self:
                    "PMT - %d" % self.relatedId if self.type == 1 else
                    "IBUG - %d" % self.relatedId,
                'statusText': lambda self:
                    self.STATUSES[self.status],
            }

            if name in computed_attributes:
                return computed_attributes[name](self)
            else:
                raise AttributeError
        except AttributeError:
            return object.__getattribute__(self, name)

    def __unicode__(self):
        return self.name
   
   
    def setStatus(self, status):
        '''
        设置状态时记录时间
        '''
        self.status = status
        self.save()

        ProjectTime(project=self, status=status, time=datetime.now()).save()

    @models.permalink
    def get_absolute_url(self):
        return ('project.views.viewDetail', [str(self.id)])


class ProjectExtend(models.Model):
    '''
    项目扩展信息
    '''
    class Meta:
        db_table = 'project_pextend'

    # 定义外键,项目id
    project = models.ForeignKey(Project, related_name="", db_column='plist_id')
    # 项目描述
    description = models.TextField(db_column='pdescribe')


class ProjectTime(models.Model):
    '''
    项目各阶段时间
    '''
    class Meta:
        db_table = 'project_ptime'

    # 定义外键,项目id
    project = models.ForeignKey(Project, related_name="", db_column='plist_id')
    # 项目状态 1：待开发  2：正在开发  3：正在测试 4：待合并 5：待上线 6：已上线
    status = models.SmallIntegerField(max_length=2, db_column='pstatus')
    # 操作人
    operator = models.IntegerField(max_length=11, db_column='poperator')
    # 进入目标状态的时间
    time = models.DateTimeField(db_column='time')


class Branch(models.Model):
    '''
    代码分支
    '''
    class Meta:
        db_table = 'project_pbranch'

    project = models.ForeignKey(Project, related_name="", db_column='plist_id')
    # 分支名称
    name = models.CharField(max_length=50, db_column='pbranchName')
    # 分支创建时间
    pcreateDateTime = models.DateTimeField(db_column='pcreateDateTime')
    # 所在dev分支
    pdevInfo = models.CharField(max_length=100, default='', db_column='pdevInfo')
    # 分支状态 1:在开发 2：已测试 3：已合并
    status = models.SmallIntegerField(max_length=2, db_column='pbranchStatus')


class RelatedPerson(models.Model):
    '''
    项目相关人
    '''
    class Meta:
        db_table = 'project_relativedperson'

    project = models.ForeignKey(Project, db_column='plist_id')
    # 员工关联的User表数据 此处不用外链的原因是 如果员工未登录系统，在User里找不到相关员工，为了更自由的发送通知，就构造了员工的冗余字段
    relatedId = models.IntegerField(max_length=10, db_column='prelatedStaffId')
    # 员工名称
    name = models.CharField(max_length=50, db_column='pstaffName')
    # 员工中文名
    chineseName = models.CharField(max_length=50, db_column='pstaffChineseName')
    # 员工Email
    email = models.EmailField(db_column='pstaffEmail')
    # 员工职位
    position = models.CharField(max_length=50, db_column='pstaffPosition')
    # 人员类型 粗略分为1产品，2开发，3测试
    type = models.SmallIntegerField(1, db_column='ptype')


class weekreports(models.Model):
    '''
    项目周报
    '''
    # 数据的类型：1.PMT异常数 2.正常PMT数 3.开发延期PMT数 4.测试延期PMT数
                #5.Hotfixs总数 6.24小时内处理 7.24~48小时处理 8.其他情况 9.刷新时间
    type = models.IntegerField(max_length=10)
    #数据所在周周一日期
    weeknum = models.IntegerField(max_length=10)
    #各类型项目数量
    num = models.IntegerField(max_length=10)


class Tasktime(models.Model):
    '''
    项目计划时间
    '''
    devtime = models.CharField(max_length=10)
    testtime = models.CharField(max_length=10)
    # 项目相关联id 可以是pmt 也可以是ibug id
    relatedId = models.IntegerField(max_length=10, db_column='prelatedId')
    exTest = models.SmallIntegerField(max_length=2)
    ifNeedDev = models.SmallIntegerField(max_length=2)


class Memo(models.Model):
    '''
    项目上线备忘
    '''
    MEMO_TYPE = (
        ('1', 'SQL - 数据库 DBRT'),
        ('2', 'SQL - 上线后数据初始化'),
        ('3', 'Job - 添加、修改 Job 调度'),
        ('4', '权限 - 添加、修改 CRM 权限'),
        ('5', '配置 - 添加、修改生产环境配置'),
        ('6', '维护 - 需要编辑/运营进行内容维护'),
        ('7','需要提前上jockjs'),
        ('8','需要提前上pages'),
        ('9', '邮件 - Pagename 有新增，发邮件至数据部'),
        ('10', '缓存 - 需清理 Memcache/Varnish'),
        ('11', '关联 - 与生产环境老版本代码无法同时运行'),
        ('12', '关联 - 与其它项目存在关联'),
        ('13', '备注')
    )

    project = models.ForeignKey(Project, db_column='project_id')
    # 备忘录类型
    type = models.SmallIntegerField(max_length=3)
    # 备忘录内容
    content = models.TextField()
    # 是否已处理
    done = models.SmallIntegerField(1)


class Cate(models.Model):
    '''
    项目分类
    '''

    name = models.CharField(max_length=50)
    parentId = models.IntegerField(max_length=10, db_column='parent_id')
    status = models.IntegerField(max_length=10)

    def __unicode__(self):
        return self.name


class ProjectCate(models.Model):
    '''
    项目-分类 关系
    '''
    class Meta:
        db_table = 'project_plist_cate'

    plist = models.ForeignKey(Project)
    cate = models.ForeignKey(Cate)
    #创建人
    creater = models.IntegerField(max_length=11)
    created = models.DateTimeField()
    status = models.SmallIntegerField(max_length=2)


class Design(models.Model):
    '''
    项目设计
    '''
    project = models.ForeignKey(Project, db_column='project_id')
    content = models.TextField()
    complete = models.IntegerField(max_length=2)
    creater = models.IntegerField(max_length=11)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    status = models.IntegerField(max_length=10)


class DesignAttach(models.Model):
    '''
    项目设计附件
    '''
    class Meta:
        db_table = 'project_design_attach'

    project = models.ForeignKey(Project, db_column='project_id')
    name = models.CharField(max_length=50)
    path = models.CharField(max_length=100)
    status = models.IntegerField(max_length=10)

class DelayInfo(models.Model):
    '''
    延期表
    '''
    class Meta:
        db_table = 'delay_info'

    # 项目id
    plist_id = models.IntegerField(max_length=11)
    # 计划上线时间
    onlineDate = models.DateField()
    # 延期时长
    delayDate = models.CharField(max_length=10)
    # 责任人
    person = models.CharField(max_length=10)
    # 延期原因
    delayReason = models.TextField()

