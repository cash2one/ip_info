from django.conf.urls import patterns, url
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^uaInfo/?$', 'uaBan.views.uaInfo', name='uaInfo'),
    url(r'^updateUa/?$', 'uaBan.views.updateUa', name='updateUa'),
    url(r'^addUaHtml/?$', 'uaBan.views.addUaHtml', name='addUaHtml'),
    url(r'^addUa/?$', 'uaBan.views.addUa', name='addUa'),
)
