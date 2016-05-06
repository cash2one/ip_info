#encoding=utf8
from django.db import models

class IpHistory(models.Model):
    class Meta:
        db_table = 'ip_history'

    ip = models.CharField(max_length=100)
    type = models.IntegerField(max_length=10)
    count = models.IntegerField(max_length=10)
    created = models.IntegerField(max_length=11)
    is_ipduan = models.IntegerField(max_length=10)

    def __unicode__(self):
        return self.ip

class ParentType(models.Model):
    class Meta:
        db_table = 'parent_type'

    desc = models.CharField(max_length=64)

    def __unicode__(self):
        return self.desc


class MonitorType(models.Model):
    class Meta:

        db_table = 'monitor_type'

    parent_id = models.IntegerField(max_length=10)
    freq = models.IntegerField(max_length=10)
    num = models.IntegerField(max_length=10)
    regex = models.CharField(max_length=100)
    hostname = models.CharField(max_length=100)
    generator = models.CharField( max_length=50)
    ipduan_select = models.IntegerField(max_length=10)
    ipduan_num = models.IntegerField(max_length=10)

    def __unicode__(self):
        return self.regex

class IpInfo(models.Model):
    class Meta:

        db_table = 'ip_info'

    ip = models.CharField(max_length=100)
    is_white = models.IntegerField(max_length=10)
    desc = models.CharField(max_length=100)
    is_del = models.IntegerField(max_length=10)
    generator = models.CharField( max_length=50)

    def __unicode__(self):
        return self.ip

