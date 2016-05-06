# -*- coding:utf-8 -*-

def is_valid_address(address):
    import re
    #p = re.compile(r'^[a-z][a-z0-9\-_\.]+@([a-z][a-z0-9\-]+\.)+[a-z]{2,3}$',re.I)
    p = re.compile(r'^[a-z0-9\-_\.]+@([a-z][a-z0-9\-]+\.)+[a-z]{2,3}$',re.I)
    if not p.match(address):
        return False
    else:
        return True

class MailAddress:
    def __init__(self, address, name='', coding='utf-8'):
        self._name = name

        if not is_valid_address(address):
            print address
            raise Exception('address is invalid!')
        else:
            self._address = address
        self._coding = coding
        return
    def __str__(self):
        from email.header import Header
        return '%s<%s>' % (str(Header(self._name,
                                      self._coding)),
                           self._address)
    def get_pure_address(self):
        return self._address
    pass

class Mail:
    def __init__(self,
                 from_address,
                 to_address,
                 subject,
                 message,
                 msg_type='html',
                 coding='utf-8'):
        if not isinstance(from_address, MailAddress):
            raise Exception('from_address is invalid!')
        self._from_address = from_address
        if isinstance(to_address, MailAddress):
            self._to_address = [to_address]
        elif type(to_address) is list:
            for addr in to_address:
                if not isinstance(addr, MailAddress):
                    raise Exception('%s of to_address is invalid!' % addr)
            self._to_address = to_address
        else:
            raise Exception('_to_address is invalid!')
        if type(subject) is not str:
            raise Exception('subject is invalid')
        if len(subject) <= 0:
            raise Exception('subject is empty!')
        self._subject = subject
        if type(message) is str:
            if len(message) <= 0:
                raise Exception('message is empty!')
            self._message = message
        elif type(message) is file:
            self._message = message.read()
        else:
            raise Exception('message is neither str nor file!')
        self._coding = coding
        self._msg_type = msg_type
        from email.mime.multipart import MIMEMultipart
        self._msg = MIMEMultipart()
        from email.header import Header
        self._msg['subject'] = Header(self._subject, charset=coding)
        self._msg['from'] = str(self._from_address)
        self._msg['to'] = ', '.join([str(i) for i in to_address])
        from email.mime.text import MIMEText
        self._msg.attach(MIMEText(self._message, self._msg_type, coding))
        return

    def __str__(self):
        return self._msg.as_string()

    def send(self, server, user='', password=''):
        import smtplib
        smtp = smtplib.SMTP(server)
        smtp.set_debuglevel(1)
        if user and password:
            smtp.login(user, password)

        _to_address = [a.get_pure_address() for a in self._to_address]
        smtp.sendmail(self._from_address.get_pure_address(), _to_address,
                      self._msg.as_string())
        smtp.close()
        return
    pass
if __name__ == '__main__':
    #a1 = MailAddress(name='吕海涛', address='htlv@aifang.com')
    #a2 = MailAddress(name='爱海涛', address='haitaolove@gmail.com')
    #a3 = MailAddress(name='海涛涛', address='ihaitao@qq.com')
    #msg = Mail(from_address=a3, to_address=[a1, a2],
    #           subject='py邮件测试',
    #           message='<h1>我是标题</h1><p>我是内容</p>')
    #msg.send(server='smtp.qq.com', user='ihaitao@qq.com', password='')
    pass
