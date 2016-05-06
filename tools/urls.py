from django.conf.urls import patterns, url
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^auction_report/?$', 'tools.views.auction_report', name='auction_report'),
)
