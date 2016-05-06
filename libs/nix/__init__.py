# -*- coding:utf-8 -*-
"""
linux系统相关的功能集合
"""
def is_vaild_user(name):
    import re
    p = re.compile(r'^[a-z_][a-z0-9_\-]{1,30}$', re.I)
    if not p.match(name):
        return False
    else:
        return True

def is_vaild_pubkey(key):
    import re
    p = re.compile(r'^ssh-rsa [a-zA-Z0-9+/=]+( [^ ]*)?$')
    if p.match(key):
        return True
    else:
        return False

def clean_workdir(func):
    """
    清理装饰器：
    根据uuid生成临时文件夹，在临时文件夹内执行目标函数，
    执行完成后删除临时文件夹

    目前只能装饰kw型参数的函数
    """
    def clean_wrapper(*args, **kwargs):
        import os
        import uuid
        import shutil
        cwd = os.getcwd()
        tmp_dir = '/tmp/' + str(uuid.uuid4())
        os.mkdir(tmp_dir)
        os.chdir(tmp_dir)
        func(*args, **kwargs)
        os.chdir(cwd)
        shutil.rmtree(tmp_dir)
        return

    return clean_wrapper

if __name__ == '__main__':
    @clean_workdir
    def hello(txt = 'abcdefg'):
        import os
        tmp = 'hello__'
        f = open(tmp, 'w')
        f.write('hello, this is htlv')
        f.close()
        f = open(tmp, 'r')
        l = f.readlines()
        print(l)
        return

    hello(txt='123456789')

