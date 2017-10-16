from django.conf import settings
from django.conf.urls import patterns, include, url
from ajax_select import urls as ajax_select_urls
from django.contrib.auth.views import login, logout_then_login
from kvalitet.views import TableauBordView
from compta.admin import cadmin

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'kvalitet.views.home', name='home'),
    # url(r'^kvalitet/', include('kvalitet.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(cadmin.urls)),
    url(r'^special-admin/', include(admin.site.urls)),
    url(r'^lookups/', include(ajax_select_urls)),

    url(r'^accounts/login/$', login),
    url(r'^accounts/logout/$', logout_then_login, name="logout"),

    #  TODO : mettre url "home"
    url(r'^$', TableauBordView.as_view(), name="gen_tableau_view"),

    url(r'^achats/', include('fchach.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )

