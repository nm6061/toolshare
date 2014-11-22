from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^register_tool/$', 'app.views.toolManagement.registerTool', name = 'registerTool'),
    url(r'^toolbox/$', 'app.views.toolManagement.toolbox', kwargs={'tool_filter': "alltools"}, name = 'toolbox'),
    url(r'^toolbox/hometools/$', 'app.views.toolManagement.toolbox', kwargs={'tool_filter': "hometools"}, name = 'hometools'),
    url(r'^toolbox/shedtools/$', 'app.views.toolManagement.toolbox', kwargs={'tool_filter': "shedtools"}, name = 'shedtools'),
    url(r'^toolbox/borrowedtools/$', 'app.views.toolManagement.toolbox', kwargs={'tool_filter': "borrowedtools"}, name = 'borrowedtools'),
    url(r'^(?P<tool_id>\d+)/$', 'app.views.toolManagement.viewTool', name='viewTool'),
    url(r'^(?P<tool_id>\d+)/update_tool/$', 'app.views.toolManagement.updateTool', name = 'updateTool'),
)
