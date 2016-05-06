# -*- coding:utf-8 -*-
"""
这是一个简单邮件报告模块，目的是与django模块集成到一起。
使用方法也很简单：
首先，引入本包
from libs.report import Report
然后实例化一个对象
report = Report(subject='',     # 报告主题，必填字段，非空
                message='',     # 报告内容，必填字段，非空，可以使用html标记
                user='',        # django用户对象，也可以是用户列表
                group='',       # django组对象，也可以是组列表
                                # user和group不能同时为空
                coding='',      # 内容编码，主题和内容需要使用相同编码，
                                # 默认为utf-8
                report_type=''  # 内容类型，默认为html，其他类型没有实现，
                                # 现在不要设置此参数
                )

需要几个配置，如下：
REPORT_SMTP_SERVER              # 邮件服务器
REPORT_SMTP_USERNAME            # 邮件服务器用户名
REPORT_SMTP_PASSWORD            # 邮件服务器用户密码
REPORT_SMTP_REPORTER_NAME       # 发件人姓名
REPORT_SMTP_REPORTER_ADDRESS    # 发件人地址
"""
from django.conf import settings
from django.contrib.auth.models import User, Group
from libs.easymail import Mail
from libs.easymail import MailAddress
from tools.models import Staff, Mygroup

class Report:
    def __init__(self, subject, message, user='', group='',
                 coding='utf-8', report_type='html'):
        if user is '' and group is '':
            raise Exception('Both user and group is empty!')
        self.user = ''
        if user is not '':
            if isinstance(user, User):
                self.user = [user]
            elif '__iter__' in dir(user):
                for u in user:
                    if not isinstance(u, User):
                        raise Exception('%s of user is not instance of User!' % u)
                self.user = user
            else:
                raise Exception('user is neither instance of User nor User list!')
        self.group = ''
        if group is not '':
            if isinstance(group, Group):
                self.group = [group]
            elif '__iter__' in dir(group):
                for g in group:
                    if not isinstance(g, Group):
                        raise Exception('%s of group is not instance of Group!' % g)
                self.group = group
            else:
                raise Exception('group is neither instance of Group nor Group list!')
        if type(subject) is str:
            if len(subject) <= 0:
                raise Exception('subject is empty!')
            self.subject = subject
        else:
            raise Exception('subject is not string!')
        if type(message) is str or type(message) is file:
            self.message = message
        else:
            raise Exception('message is neither string nor file object!')
        self.coding = coding
        self.report_type = report_type
        self.smtp_server = settings.REPORT_SMTP_SERVER
        self.smtp_username = settings.REPORT_SMTP_USERNAME
        self.smtp_password = settings.REPORT_SMTP_PASSWORD
        self.mail_from = MailAddress(name=settings.REPORT_SMTP_REPORTER_NAME,
                                     address=settings.REPORT_SMTP_REPORTER_ADDRESS)
        pass
    def build_header(self):
        single_user = ''
        group = ''
        if self.user:
            single_user = '，'.join([(u.first_name and 
                                       [u.first_name.encode(self.coding)] 
                                       or [u.username.encode(self.coding)])[0] + '同学' 
                                      for u in self.user])
        if self.group:
            group = '，'.join([g.name.encode(self.coding) + '组的同学' 
                              for g in self.group])
        self.header = '<b>%s，%s</b><hr/>' % (single_user, group)
        pass
    def build_rcpt_list(self):
        users = set()
        if self.user:
            users = users.union(set(self.user))
        if self.group:
            for g in self.group:
                users = users.union(set(User.objects.filter(groups__name=g.name)))

        self.rcpt_list = [MailAddress(name=(u.first_name 
                                          and [u.first_name.encode(self.coding)] 
                                          or [u.username.encode(self.coding)])[0], 
                                    address=u.email) 
                        for u in users if u.email]
        pass
    def send(self):
        self.build_header()
        self.build_rcpt_list()
        msg = self.header + self.message
        mail = Mail(from_address=self.mail_from, to_address=self.rcpt_list,
                    subject=self.subject, message=msg)
        print self.smtp_server
#        print self.smtp_username
#        print self.smtp_password
        pass
        mail.send(server=self.smtp_server,
                  user=self.smtp_username,
                  password=self.smtp_password)
        pass

if __name__ == '__main__':
    pass

'''
新邮件提醒
'''
class SendGroupMail:
    def __init__(self, subject, message, user='', group='',
                 coding='utf-8', report_type='html'):
        if user is '' and group is '':
            raise Exception('Both user and group is empty!')
        self.user = ''
        if user is not '':
            if isinstance(user, Staff):
                self.user = [user]
            elif '__iter__' in dir(user):
                for u in user:
                    if not isinstance(u, Staff):
                        raise Exception('%s of user is not instance of User!' % u)
                self.user = user
            else:
                raise Exception('user is neither instance of User nor User list!')
        self.group = ''
        if group is not '':
            if isinstance(group, Mygroup):
                self.group = [group]
            elif '__iter__' in dir(group):
                for g in group:
                    if not isinstance(g, Mygroup):
                        raise Exception('%s of group is not instance of Group!' % g)
                self.group = group
            else:
                raise Exception('group is neither instance of Group nor Group list!')
        if type(subject) is str:
            if len(subject) <= 0:
                raise Exception('subject is empty!')
            self.subject = subject
        else:
            raise Exception('subject is not string!')
        if type(message) is str or type(message) is file:
            self.message = message
        else:
            raise Exception('message is neither string nor file object!')
        self.coding = coding
        self.report_type = report_type
        self.smtp_server = settings.REPORT_SMTP_SERVER
        self.smtp_username = settings.REPORT_SMTP_USERNAME
        self.smtp_password = settings.REPORT_SMTP_PASSWORD
        self.mail_from = MailAddress(name=settings.REPORT_SMTP_REPORTER_NAME,
                                     address=settings.REPORT_SMTP_REPORTER_ADDRESS)
        pass
    def build_header(self):
        single_user = ''
        group = ''
        if self.user:
            single_user = ' '.join([u.name.encode(self.coding) + '同学,' 
                                      for u in self.user])
        if self.group:
            group = ' '.join([g.name.encode(self.coding) + '组的同学:' 
                              for g in self.group])
        headerString = single_user.join(group)
        self.header = '<b>%s</b><hr/>' % (headerString)
        pass
    def build_rcpt_list(self):
        users = set()
        if self.user:
            users = users.union(set(self.user))
        if self.group:
            for g in self.group:
                users = users.union(Staff.objects.filter(mygroup=g,job_status=0))

        self.rcpt_list = [MailAddress(name=[u.name.encode(self.coding)][0],address=u.email) 
                        for u in users if u.email]
        pass
    def send(self):
        self.build_header()
        self.build_rcpt_list()
        msg = self.header + self.message
        mail = Mail(from_address=self.mail_from, to_address=self.rcpt_list,
                    subject=self.subject, message=msg)
        pass
        mail.send(server=self.smtp_server, user=self.smtp_username, password=self.smtp_password)
        pass