# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import get_models, get_app
from fchach.models import FchAch


class FchAchAdmin(admin.ModelAdmin):
    list_display=('id', 'titre', 'fournisseur', 'client', 'created_by')

'''
On enregistre tout les modèles de fchach
'''

for model in get_models(get_app('fchach')):
    admin.site.register(model)

admin.site.unregister(FchAch)
admin.site.register(FchAch, FchAchAdmin)
