#encoding=utf-8
'''
Created on 2013-7-14

@author: kyou
'''
from deploy.models import Version
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from profile.models import Activity, ActivityImage
import time

class Service:
    #当前安居客线上列表
    @staticmethod
    def list_anjuke_online_version(page):
        list = Version.objects.filter(type=1).order_by("-name")
        '''
        版本列表
        '''
        versions = Paginator(list, 10).page(page)
    
        for version in versions:
            version.generator = User.objects.get(id=version.generator) if version.generator else None
            version.publisher = User.objects.get(id=version.publisher) if version.publisher else None
        return versions

        
