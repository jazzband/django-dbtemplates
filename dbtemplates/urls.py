from django.conf.urls.defaults import *

if 'tinymce' in settings.INSTALLED_APPS:
    urlpatterns += patterns('', url(r'^tinymce/', include('tinymce.urls')))
