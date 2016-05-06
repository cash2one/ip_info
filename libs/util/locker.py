#encoding=utf8

import os
import md5

'''
通过生成临时锁文件来实现的简单的锁
'''


def hasLocked(lockSpace):
    LockName = '/tmp/' + md5.new(lockSpace).hexdigest() + '.lock'

    return os.path.isfile(LockName)


def lock(lockSpace):
    LockName = '/tmp/' + md5.new(lockSpace).hexdigest() + '.lock'
    open(LockName, 'w').close()


def unlock(lockSpace):
    LockName = '/tmp/' + md5.new(lockSpace).hexdigest() + '.lock'
    if os.path.isfile(LockName):
        os.remove(LockName)
