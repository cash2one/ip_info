#encoding=utf8
from django.db import models

class UaInfo(models.Model):
    class Meta:

        db_table = 'ua_info'

    user_agent = models.CharField(max_length=100)
    is_del = models.IntegerField(max_length=10)
    generator = models.CharField( max_length=50)

    def __unicode__(self):
        return self.user_agent

