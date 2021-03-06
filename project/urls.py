from django.conf.urls import patterns, url
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$','project.views.projects'),
    url(r'^create','project.views.create'),
    url(r'^detail/(\d+)/','project.views.viewDetail'),
    url(r'^mod/?','project.views.modifyOnlineDate'),
    url(r'^today/','project.views.pendingProjects', {'type': 'today'}),
    url(r'^tomorrow/','project.views.pendingProjects', {'type': 'tomorrow'}),
    url(r'^week/','project.views.pendingProjects', {'type': 'week'}),
    url(r'^delayed/','project.views.pendingProjects', {'type': 'delayed'}),
    url(r'^reports/','project.views.reports'),
    url(r'^report/(\d+)/','project.views.report'),
    url(r'^my/$','project.views.myProjects'),
    url(r'^archive/$','project.views.archivedProjects'),
    url(r'^dispatch','project.views.dispatch'),
    url(r'^memoCreate/(\d+)/','project.views.createMemo'),
    url(r'^memoModify/(\d+)/','project.views.modifyMemo'),
    url(r'^reportsflash/','project.views.reportsflash'),
    url(r'^cate/list/?','project.viewsext.catelist'),
    url(r'^cate/add/?','project.viewsext.cateadd'),
    url(r'^cate/delete/?','project.viewsext.catedelete'),
    url(r'^cate/childrenlist/?','project.viewsext.catechildrenlist'),
    url(r'^design/create/(\d+)?/?','project.viewsext.designcreate'),
    url(r'^design/detail/(\d+)?/?','project.viewsext.designdetail'),
    url(r'^design/delete/(\d+)?/?','project.viewsext.designdelete'),
    url(r'^design/attach/delete/(\d+)?/?','project.viewsext.deleteattach'),
    url(r'^updateHtml/?$', 'project.views.updateHtml'),
    url(r'^delay_project/?','project.views.delay_project'),
    url(r'^delayHtml/?$', 'project.views.delayHtml'),
    url(r'^add_delay/?$', 'project.views.add_delay'),
    url(r'^success/?$', 'project.views.success'),
)
