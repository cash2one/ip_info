# -*- coding: utf-8 -*-
#
from django.conf.urls import patterns, url
from compare import views


#路由模块
urlpatterns = patterns('',                                  
    url(r'^index$', views.index),                              
    url(r'^add$', views.add), 
    url(r'^modify/(\d+)$', views.modify), 
    url(r'^delete/(\d+)$', views.delete),       
    url(r'^diff/(\d+)$', views.diff),
    url(r'^getContent/(.)/(\d+)$', views.getContent), 
    url(r'^clear/(\d+)$', views.clear),
    url(r'^clearAll$', views.clearAll),
    url(r'^delAll$', views.delAll),
)
