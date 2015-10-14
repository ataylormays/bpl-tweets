from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

# Examples:
# url(r'^$', 'epl_twitter.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^home/', include('tweets.urls_home')),
    url(r'^about/', include('tweets.urls_about')),
    url(r'^contact/', include('tweets.urls_contact')),
    url(r'^teams/', include('tweets.urls')),
    url(r'^live/', include('tweets.urls_live')),
    url(r'^archive/', include('tweets.urls_archive')),
    url(r'^demo/', include('tweets.urls_demo')),
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
