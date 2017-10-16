# -*- coding: utf-8 -*-

from django.views.generic import CreateView, UpdateView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from kvalitet.abstract_models import FchQualHistory
from compta.models import Service, Ligne, Directeur, Comptable

class LoggedInView(object):
    """
    Classe abstraite pour login
    Puisque toutes les vues héritent de cette classe, on y ajoute quelques méthodes pratiques...
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInView, self).dispatch(*args, **kwargs)

    def roles(self):
        """
        Méthode pour renvoyer les équipes dont l'utilisateur est chef ou tresorier
        """
        return {'tresorier': list(Service.objects.filter(tresorier=self.request.user.id)),\
                'chef': list(Service.objects.filter(chef=self.request.user.id)), \
                'resp_ligne': list(Ligne.objects.filter(responsable=self.request.user.id)),
                'directeur': list(Directeur.objects.filter(directeur=self.request.user.id)),
                'comptable': list(Comptable.objects.filter(comptable=self.request.user.id))}

    def documents_context(self, context, model_documents):
        """
        Methode pour récupérer les documents associés à une fiche et les ajouter au contexte
        """
        context['documents'] = model_documents.objects.filter(fchqual = context[self.context_object_name].id)
        return context

    def history_context(self, context, model_history):
        """
        Méthodes pour récupérer l'historique d'une fiche et les ajouter au contexte
        """
        if isinstance(self.object, FchQualHistory):
            context['history'] = model_history.objects.filter(fchqual = self.object.fchqual.id).order_by('-version')
        else:
            context['history'] = model_history.objects.filter(fchqual = self.object.id).order_by('-version')
        return context

    def next_user_context(self, context, model):
        context['next_user_'+model.context_string] = model.objects.filter(next_user=self.request.user.id).exclude(state=-1)
        return context

class FchQualDetailView(LoggedInView, DetailView):
    """
    Classe abstaite pour les vues détails
    """
    def get_object(self, *args, **kwargs):
        """
        Vérification des permissions
        """
        obj = super(FchQualDetailView, self).get_object(*args, **kwargs)
        if obj.permissions.can_view(obj, self.request.user, self.roles()):
            return obj
        else:
            raise PermissionDenied()

class FchQualCreateView(LoggedInView, CreateView):
    """
    Classe abstraite pour la création de fiche qualité
    """
    def form_valid(self, form):
        """
        Ajoute l'utilisateur connecté, modifie l'état et upload les fichiers si nécessaire
        """
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.modified_by = self.request.user
        obj.save()
        if form.cleaned_data['fichiers']:
            map(lambda a: form.documents(user=self.request.user,doc=a,fchqual=obj).save(), form.cleaned_data['fichiers'])
        self.specific_valid(obj, form)
        obj.state, obj.cookie, obj.next_user = obj.workflow.states[obj.state][0](obj, user=self.request.user)
        obj.save()
        return HttpResponseRedirect(self.success_url)

class FchQualUpdateView(LoggedInView, UpdateView):
    """
    Classe abstraite pour la modification de fiche qualité
    """
    def get_object(self, *args, **kwargs):
        """
        Vérification des permissions
        """
        obj = super(FchQualUpdateView, self).get_object(*args, **kwargs)
        if obj.permissions.can_edit(obj, self.request.user, self.roles()) or \
            obj.permissions.can_validate(obj, self.request.user, self.roles()) or \
            obj.permissions.can_mod_line(obj, self.request.user, self.roles()) or \
            obj.permissions.can_mod_emplacement(obj, self.request.user, self.roles()) :
            return obj
        else:
            raise PermissionDenied()

    def form_valid(self, form):
        """
        Ajoute l'utilisateur connecté, et modifie l'état.
        """
        obj = form.save(commit=False)
        obj.version = obj.version + 1
        obj.modified_by = self.request.user
        accept = int(self.request.POST.get('accept', 0))
        obj.save()
        for file_id in self.request.POST.getlist('del_doc'):
           form.documents.objects.get(pk=file_id).delete()
        if form.cleaned_data['fichiers']:
            map(lambda a: form.documents(user=self.request.user,doc=a,fchqual=obj).save(), form.cleaned_data['fichiers'])
        self.specific_valid(obj, form)
        if obj.state != -1:
            obj.state, obj.cookie, obj.next_user = \
                    obj.workflow.states[obj.state][0](obj, accept=accept,user=self.request.user)
        obj.save()
        return HttpResponseRedirect(self.success_url)
