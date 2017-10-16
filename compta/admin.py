# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import get_models, get_app
from kvalitet.forms import UserChoiceField
from compta.models import Service, Ligne, Fournisseur, Tutelle, Entite, MatiereXlab, Nomenclature
from compta.views import ImportFournisseurView
from django import forms
from django.conf.urls import patterns, url


class CadminAdmin(admin.ModelAdmin):
      change_list_template = "admin/compta/cadmin_change_list.html"


class MatiereXlabAdmin(CadminAdmin):
    pass

class TutellesAdmin(CadminAdmin):
    pass

class EntiteAdmin(CadminAdmin):
    pass

class NomenclatureAdmin(CadminAdmin):
    pass

class LigneAdminForm(forms.ModelForm):
    """
    Classe Form pour Ligne
    """
    responsable = UserChoiceField(queryset=User.objects.all().order_by('last_name'))
    class Meta:
          model = Ligne

class LigneAdmin(CadminAdmin):
      form = LigneAdminForm


class ServiceAdminForm(forms.ModelForm):
    """
    Classe Form pour Service
    """
    tresorier = UserChoiceField(queryset=User.objects.all().order_by('last_name'))
    chef = UserChoiceField(queryset=User.objects.all().order_by('last_name'))
    secretaire = UserChoiceField(queryset=User.objects.all().order_by('last_name'))
    class Meta:
          model = Service

class ServiceAdmin(CadminAdmin):
    form = ServiceAdminForm


class FournisseurAdmin(CadminAdmin):
    change_list_template = "admin/compta/cadmin_change_list.html"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MyAdminSite(admin.sites.AdminSite):
    def get_urls(self):
        urls = super(MyAdminSite, self).get_urls()
        my_urls = patterns('',
                url(r'compta/import-fournisseurs/$',self.admin_view(ImportFournisseurView.as_view()),
                                                    name='import-fournisseurs' ),
                )
        return my_urls + urls

cadmin = MyAdminSite(name='cadmin')

'''
On enregistre tout les modèles de compta pour les sites admin
'''

for model in get_models(get_app('compta')):
    admin.site.register(model)

'''
et seulement quuns pour cadmin
'''

cadmin.register(Nomenclature, NomenclatureAdmin)
cadmin.register(MatiereXlab, MatiereXlabAdmin)
cadmin.register(Entite, EntiteAdmin)
cadmin.register(Tutelle, TutellesAdmin)
cadmin.register(Service, ServiceAdmin)
cadmin.register(Ligne, LigneAdmin)
cadmin.register(Fournisseur, FournisseurAdmin)

