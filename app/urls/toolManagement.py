from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^register_tool/$', 'app.views.toolManagement.registerTool', name = 'registerTool'),
    url(r'^(?P<tool_id>\d+)/$', 'app.views.toolManagement.viewTool', name='viewTool'),
    url(r'^(?P<tool_id>\d+)/update_tool/$', 'app.views.toolManagement.updateTool', name = 'updateTool'),
)
