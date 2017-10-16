# -*- coding: utf-8 -*-

from django.forms.util import ErrorList
from django import forms
from django.views.generic import FormView
from django.forms.fields import FileField
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from compta.models import Fournisseur

class ImportFournisseurForm(forms.Form):
    fichier = FileField()

class ImportFournisseurView(FormView):
    template_name="admin/compta/cadmin_import_form.html"
    form_class=ImportFournisseurForm
    success_url = reverse_lazy('cadmin:compta_fournisseur_changelist')

    def get_context_data(self, **kwargs):
        context = super(ImportFournisseurView, self).get_context_data(**kwargs)
        #import ipdb; ipdb.set_trace()
        return context

    def form_valid(self, form, *args, **kwargs):
        Fournisseur.objects.all().update(active=False)
        try:
            for line in form.cleaned_data['fichier']:
                obj, created = Fournisseur.objects.get_or_create(nom=line.split('\t')[1].decode('latin1'),
                                                                siret=line.split('\t')[3].decode('latin1'))
                obj.active=True
                obj.save()
        except Exception:
            # Crado : on devrait faire le check dans un clean
            form._errors["fichier"] = ErrorList(["Le fichier n'est pas au bon format"])
            return self.form_invalid(form, *args, **kwargs)
        return HttpResponseRedirect(self.success_url)


