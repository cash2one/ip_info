from django.conf.urls import patterns, url
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^list/?$', 'ipBan.views.list', name='list'),
    url(r'^rule/?$', 'ipBan.views.rule', name='rule'),
    url(r'^ipInfo/?$', 'ipBan.views.ipInfo', name='ipInfo'),
    url(r'^addIpHtml?$', 'ipBan.views.addIpHtml', name='addIpHtml'),
    url(r'^addIp?$', 'ipBan.views.addIp', name='addIp'),
    url(r'^updateIp?$', 'ipBan.views.updateIp', name='updateIp'),
    url(r'^ipAdmin/$', 'ipBan.views.ipAdminHtml', name='ipAdmin'),
    url(r'^addRuleHtml?$', 'ipBan.views.addRuleHtml', name='addRuleHtml'),
    url(r'^addRule?$', 'ipBan.views.addRule', name='addRule'),
    url(r'^ajax/?$', 'ipBan.views.ajax', name='ajax'),
)
