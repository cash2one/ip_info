# -*- coding: utf-8 -*-

from django.db import models

#记录模型
class Record(models.Model):
    aurl = models.CharField('AURL', max_length=150)
    burl = models.CharField('BURL', max_length=150)
    desc = models.CharField('备注', blank=True, max_length=100)
    astatus = models.IntegerField('AURL的內容状态')
    bstatus = models.IntegerField('BURL的内容状态')
    acoutent = models.TextField('AURL的HTML', blank=True )
    bcoutent = models.TextField('BURL的HTML', blank=True )
    diff = models.TextField('比较结果', blank=True )
    result = models.IntegerField('结果')
    
    def __unicode__(self):
        return self.desc
            


