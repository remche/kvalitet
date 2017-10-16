# -*- coding: utf-8 -*-
from django import forms

class UserChoiceField(forms.ModelChoiceField):
    """
    Classe qui permet d'afficher la liste déroulante d'utilisateur en mode nom prenom
    """
    def label_from_instance(self, obj):
         return "%s %s" % (obj.last_name, obj.first_name)


