# -*- coding: utf-8 -*-
import ho.pisa as pisa
import cStringIO as StringIO
from fchach.models import  FchAch, FchAchHistory, FchAchDoc , FchAchProd
from compta.models import Nomenclature, MatiereXlab
from fchach.forms import FchAchCreateForm, FchAchUpdateForm, FchAchLineForm, FchAchValidateForm, FchAchEmplacementForm
from kvalitet.abstract_views import  FchQualUpdateView, FchQualCreateView, FchQualDetailView, LoggedInView
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string

def create_prod(self, obj, form):
    FchAchProd.objects.filter(fchach=obj).delete()
    for produit in form.cleaned_data['produits'].values():
        FchAchProd(produit=produit['intitule'], prixht=produit['prix'].replace(',','.'), quantite=produit['quantite'] ,fchach=obj, \
                    matiere_xlab=MatiereXlab.objects.get(id=produit['matiere']), nomenclature=Nomenclature.objects.get(id=produit['nomenclature']) \
                ).save()

def custom_context(self, context):
        context = super(type(self), self).next_user_context(context, FchAch)
        context['view_type_menu'] = 'achats'
        context['client_fchach'] = FchAch.objects.filter(client=self.request.user).exclude(state=-1)
        context['closed_fchach'] = FchAch.objects.filter(created_by=self.request.user, state=-1)
        if not isinstance(self, ListView):
            context['fchach_list'] = FchAch.objects.filter(created_by=self.request.user)
        return context

class FchAchCreateView(FchQualCreateView):
    form_class = FchAchCreateForm
    template_name="fchach/fchach_create.html"
    success_url='.'

    specific_valid = create_prod

    def get_context_data(self, **kwargs):
        context = super(FchAchCreateView, self).get_context_data(**kwargs)
        context = custom_context(self, context)
        # Pour le menu collapse
        context['view_type_menu'] = 'actions'
        context['need_js_form'] = True
        return context

class FchAchUpdateView(FchQualUpdateView):
    model = FchAch
    context_object_name = "fchach"
    success_url='/achats/'

    specific_valid = create_prod

    def get_form_class(self):
        context = super(FchAchUpdateView, self).get_context_data()
        form_class = FchAchValidateForm
        if context[self.context_object_name].permissions.can_mod_line(context[self.context_object_name], self.request.user, self.roles()):
            form_class = FchAchLineForm
        elif context[self.context_object_name].permissions.can_edit(context[self.context_object_name], self.request.user, self.roles()) :
            form_class = FchAchUpdateForm
        elif context[self.context_object_name].permissions.can_mod_emplacement(context[self.context_object_name], self.request.user, self.roles()) :
            form_class = FchAchEmplacementForm
        return form_class

    def get_context_data(self, **kwargs):
        context = super(FchAchUpdateView, self).get_context_data(**kwargs)
        context = custom_context(self, context)
        context['roles'] = super(FchAchUpdateView, self).roles()
        context['produits'] = FchAchProd.objects.filter(fchach = context[self.context_object_name].id)
        context['need_js_form'] = True
        return context

class FchAchListView(LoggedInView, ListView):
    context_object_name="fchach_list"
#    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(FchAchListView, self).get_context_data(**kwargs)
        context = custom_context(self, context)
        return context

    def get_queryset(self):
            return FchAch.objects.filter(created_by=self.request.user).exclude(state=-1).order_by('-state')

class TableauBordView(FchAchListView):
    template_name = "fchach/tableaubord.html"

class FchAchDetailView(FchQualDetailView):
    model = FchAch
    context_object_name = "fchach"

    def get_context_data(self, **kwargs):
        context = super(FchAchDetailView, self).get_context_data(**kwargs)
        context =  super(FchAchDetailView, self).history_context(context, FchAchHistory)
        context =  super(FchAchDetailView, self).documents_context(context, FchAchDoc)
        context = custom_context(self, context)
        context['roles'] = super(FchAchDetailView, self).roles()
        context['produits'] = FchAchProd.objects.filter(fchach = context[self.context_object_name].id)
        return context

class FchAchDetailVersionView(FchAchDetailView):
    template_name = "fchach/fchach_detail.html"

    def get_object(self):
        return get_object_or_404(FchAchHistory, id = FchAchHistory.objects.filter(fchqual=self.kwargs['pk'])
                                                                            .filter(version=self.kwargs['version'])[0].id)

    def get_context_data(self, **kwargs):
        context = super(FchAchDetailVersionView, self).get_context_data(**kwargs)
        context['produits'] = FchAchProd.objects.filter(fchach = context[self.context_object_name].fchqual)
        return context

class FchAchPDFView(FchAchDetailView):
    def render_to_response(self, context, **kwargs):
        #TODO: ne générer un pdf que si la fiche est en état clos. sinon, permissiondenied
        result = StringIO.StringIO()
        pisa.pisaDocument(render_to_string("fchach/fchach_pdf.html", context), result)
        response = HttpResponse(result.getvalue(), mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Fiche Achat %(num)s.pdf"' % { 'num': self.object.id }
        return response
