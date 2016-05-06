#encoding=utf-8
import os

from django.conf import settings

'''
Created on 2012-7-9
封装查找数据库方法
@author: lenye01
'''
'''
连接数据库
返回连接符
'''
class db:

    host = ''
    passwd = ''
    user = ''
    db = ''
    port = ''

    def __init__(self, set=''):
        if set and set in settings.DATABASES:
            config = settings.DATABASES[set]
        else:
            config = settings.DATABASES['default']

        self.host = config['HOST']
        self.user = config['USER']
        self.passwd = config['PASSWORD']
        self.port = config['PORT']
        self.db = config['NAME']

        self.connect()

    def connect(self):
        import MySQLdb
        self.conn = MySQLdb.connect(host=self.host, user=self.user,
                                    passwd=self.passwd, db=self.db, port=self.port)
        cursor = self.conn.cursor()
        cursor.execute("set charset utf8")
        cursor.close()
        return

    def execute(self, sql):
        '''
        执行sql语句
        '''
        from exceptions import Warning
        if sql != '':
            cursor = self.conn.cursor()
            cursor.execute(sql)
        else:
            raise Warning('You Have Not Input Any SQL')

    def findBySql(self, sql):
        '''
        通过sql获取数据
        '''
        from exceptions import Warning
        if sql != '':
            cursor = self.conn.cursor()
            try:
                cursor.execute(sql)
            except:
                print sql
            lines = cursor.fetchall()
            cursor.close()
            return lines
        else:
            raise Warning('You Have Not Input Any SQL')

    def importIn(self, source, database):
        '''
        导入文件到数据库
        '''
        handler = os.popen(
            "zcat %s | mysql -h%s --port=%s -u%s -p%s " % (source + '.gz', self.host, self.port, self.user, self.passwd)
        )
        print "zcat %s | mysql -h%s --port=%s -u%s -p%s " % (source + '.gz', self.host, self.port, self.user, self.passwd)
        return handler.readlines()

    def dump(self, to, database, table, where=''):
        '''
        导出
        '''
        where = where or '1'

        os.popen("echo CREATE DATABASE IF NOT EXISTS \`%s\`\; >> %s" % (database, to))
        os.popen("echo USE \`%s\`\; >> %s" % (database, to))
        handler = os.popen('''
            mysqldump -h%s --port=%s -u%s -p%s \
            --lock-tables=false \
            --add-drop-table \
            --skip-add-locks \
            --skip-comments \
            --dump-date \
            --compress \
            --force \
            --where '%s' \
            --databases %s \
            --tables %s \
            >> %s''' % (self.host, self.port, self.user, self.passwd, where, database, table, to))

        return handler.readlines()


if __name__ == '__main__':
    pass
