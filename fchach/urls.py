from django.conf.urls import patterns, url

#from dajaxice.core import dajaxice_autodiscover
#dajaxice_autodiscover()

#from django.conf import settings

#from django.views.generic import ListView
#from fchach.models import FchAchRecord

from fchach.views import FchAchListView, FchAchCreateView, FchAchDetailView, FchAchDetailVersionView, FchAchUpdateView, \
                            FchAchPDFView, TableauBordView

urlpatterns = patterns('',
    url(r'^$', TableauBordView.as_view(), name="fchach_tableau_view"),
    url(r'^mes-fiches$', FchAchListView.as_view(), name="fchach_my_list_view"),
    url(r'^fiches-client$', FchAchListView.as_view(), name="fchach_client_list_view"),
    url(r'^en-attente$', FchAchListView.as_view(), name="fchach_attente_list_view"),
    url(r'^closed$', FchAchListView.as_view(), name="fchach_closed_list_view"),
    url(r'^new$', FchAchCreateView.as_view(), name="fchach_new_view"),
    url(r'^view/(?P<pk>\d+)/$', FchAchDetailView.as_view(), name="fchach_detail_view"),
    url(r'^view/(?P<pk>\d+)/pdf$', FchAchPDFView.as_view(), name="fchach_pdf_view"),
    url(r'^view/(?P<pk>\d+)/(?P<version>\d+)/$', FchAchDetailVersionView.as_view(), name="fchach_detail_version_view"),
    url(r'^edit/(?P<pk>\d+)/$', FchAchUpdateView.as_view(), name="fchach_edit_view"),
)
