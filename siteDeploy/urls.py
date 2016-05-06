from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import patterns, include, url
from django.contrib import  admin


#admin.autodiscover()
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$','siteDeploy.views.home'),
    url(r'^login','account.views.login'),
    url(r'^logout','account.views.logout'),
    url(r'^ipBan/',include('ipBan.urls')),
    url(r'^uaBan/',include('uaBan.urls')),
    url(r'^tools/',include('tools.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^compare/', include('compare.urls')),
    url(r'^index/','index.views.index'),
)
urlpatterns += staticfiles_urlpatterns()

handler404 = 'siteDeploy.views.page404'
handler500 = 'siteDeploy.views.pageError'
