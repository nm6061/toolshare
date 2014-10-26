from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^registerTool/$', 'app.views.toolManagement.registerTool', name = 'registerTool'),
    url(r'^(?P<tool_id>\d+)/$', 'app.views.toolManagement.viewTool', name='viewTool'),
)
