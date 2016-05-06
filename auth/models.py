#encoding=utf-8
from django.db import models

#对应 auth_user_groups model
class user_groups(models.Model):
     user_id = models.IntegerField()
     group_id = models.IntegerField()