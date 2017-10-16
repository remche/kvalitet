# -*- coding: utf-8 -*-

from compta.models import Service, Ligne, Directeur, Comptable
import fchach
from fchach.tasks import build_and_send_mail
from django.template import Context
import os, base64
from django.contrib.sites.models import Site

class FchAchWorkflow:
    """
    Classe pour la gestion du workflow
    States est un dictionnaire avec un pointeur sur fonction + la chaîne descriptive pour chaque état
    Chaque méthode construit le context pour envoyer l'email
    """
    def __init__(self):
        self.states = { 0 : [self.new,"Nouvelle"],
                       1 : [self.tresorier, "En attente de validation par le trésorier"],
                       2 : [self.compta, "À la comptabilité"],
                       3 : [self.direction, "En attente de validation par la direction"],
                       4 : [self.commande, "Bon de commande"],
                       -1 : [self.closed, "Close (bon de commande prêt)"],
                 }

    def build_context(self, obj, state, role, user=None):
        """
        Méthode commune pour le contexte
        """
        context=Context()
        context['current_site'] = Site.objects.get_current()
        if user:
            context['user'] = user
        context['key'] = base64.urlsafe_b64encode(os.urandom(20))
        context['client'] = obj.client
        context['tres'] = Service.objects.get(pk=obj.team.id).tresorier
        context['chef'] = Service.objects.get(pk=obj.team.id).chef
        if obj.ligne:
            context['resp_ligne'] = Ligne.objects.get(pk=obj.ligne.id).responsable
        context['directeur'] = Directeur.objects.get(pk=1).directeur
        context['comptable'] = Comptable.objects.get(pk=1).comptable
        context['fchach'] = obj
        context['state'] = state
        context['role'] = role
        context['produits'] = fchach.models.FchAchProd.objects.filter(fchach = obj.id)
        return context

    def build_obslist(self, obj, context, createur=True, client = True, tresorier=True, chef=True, directeur=False, comptable=False, resp_ligne=True):
        obs = []
        if createur:
            obs += [ (u"créateur de la fiche ci-dessous ", obj.created_by.email) ]
        if client:
            obs += [ (u"client de la commande ci-dessous ", obj.client.email) ]
        if tresorier:
            obs += [ (u"trésorier d'équipe", context['tres'].email) ]
        if chef:
            obs += [ (u"chef d'équipe", context['chef'].email) ]
        if directeur:
            obs += [ ("directeur du laboratoire", context['directeur'].email) ]
        if comptable:
            obs += [ ("comptable", context['comptable'].email) ]
        if resp_ligne:
            obs += [("responsable de ligne", context['resp_ligne'].email)]
        return obs



    def new(self, obj, accept=1, user=None):
        """
        Nouvelle fiche achat
        """
        # Appelé depuis autres étapes du wf :
        # La fiche n'a pas été acceptée, on envoit un mail au créateur, et repart en étape 0.
        if accept == -1:
            context = self.build_context(obj, 0, "créateur", obj.created_by)
            obs = self.build_obslist(obj, context, client = False, resp_ligne=("resp_ligne" in context))
            build_and_send_mail(context, obj.created_by, obs)
            return context['state'], context['key'], obj.created_by

        # L'utilisateur est le trésorier et la ligne est spécifiée, on passe l'étape 1.
        if user == Service.objects.get(pk=obj.team.id).tresorier and accept == 1 and obj.ligne:
            return self.tresorier(obj, 1, user)
        # Sinon, on envoie le mail au trésorier et aux observateurs
        else:
            context = self.build_context(obj, 1, "trésorier", user)
            obs = self.build_obslist(obj, context, client = False, tresorier= False, resp_ligne=("resp_ligne" in context))
            build_and_send_mail(context, context['tres'], obs)
            return context['state'], context['key'], context['tres']

#    def client(self, obj, accept=0, user=None):
#        """
#        Validation par le client
#        """
#        if user == obj.client:
#            if accept == 1:
#                # Le client est aussi le trésorier, on passe l'étape 2.
#                if user == Service.objects.get(pk=obj.team.id).tresorier:
#                    return self.tresorier(obj, 1, user)
#                else:
#                    # Sinon, on envoie un mail au trésorier et aux observateurs
#                    context = self.build_context(obj, 2, "tresorier", user)
#                    obs = [ obj.created_by.email, context['client'].email, \
#                        context['chef'].email, context['resp_ligne'].email, \
#                        context['directeur'].email, context['comptable'].email ]
#                    build_and_send_mail(context, context['tres'], obs)
#                    return context['state'], context['key'], context['tres']
#            # La fiche est refusé, retour à l'étape  0
#            elif accept == -1:
#                return self.new(obj, -1, user)
#        return self.new(obj, 0, user)

    def tresorier(self, obj, accept=-1, user=None):
        """
        Trésorier
        """
        if user == Service.objects.get(pk=obj.team.id).tresorier:
            if accept == 1:
                # Le tresorier est aussi le comptable
                if Comptable.objects.filter(comptable=user.id):
                    return self.compta(obj, 1, user)
                else:
                    # Sinon, envoie un mail au comptable et aux observateurs
                    context = self.build_context(obj, 2, "comptable", user)
                    obs = self.build_obslist(obj, context, tresorier= False, comptable=False)
                    build_and_send_mail(context, context['comptable'], obs)
                    return context['state'], context['key'], context['comptable']
            elif accept == -1:
                return self.new(obj, -1, user)

    def compta(self, obj, accept=-1, user=None):
        """
        Comptable
        """
        if Comptable.objects.filter(comptable=user.id):
            if  accept == 1 :
                context = self.build_context(obj, 3, "directeur", user)
                obs = self.build_obslist(obj, context, comptable=False)
                build_and_send_mail(context, context['directeur'], obs)
                return context['state'], context['key'], context['directeur']
            elif accept == -1:
                return self.new(obj, -1, user)

#    def resp_ligne(self, obj, accept=0, user=None):
#        """
#        Responsable de la ligne : s'il est aussi directeur, étape suivante
#        """
#        if user == Ligne.objects.get(pk=obj.ligne.id).responsable:
#            if accept == 1:
#                if Directeur.objects.filter(directeur=user.id) and accept == 1:
#                    return self.direction(obj, 1, user)
#                else:
#                    context = self.build_context(obj, 4, "directeur", user)
#                    return context['state'], context['key'], context['directeur']
#            elif accept == -1:
#                return self.new(obj, -1, user)
#        return self.tresorier(obj, 1, user)

    def direction(self, obj, accept=-1, user=None):
        """
        Direction
        """
        if Directeur.objects.filter(directeur=user.id):
            if accept == 1:
                context = self.build_context(obj, 4, "comptable", user)
                obs = self.build_obslist(obj, context)
                build_and_send_mail(context, context['comptable'], obs)
                return context['state'], context['key'], context['comptable']
            elif accept == -1:
                return self.new(obj, -1, user)

    def commande(self, obj, accept=-1, user=None):
       """
        Comptable
        """
       if Comptable.objects.filter(comptable=user.id):
            if  accept == 1 :
                context = self.build_context(obj, -1, "", user)
                obs = self.build_obslist(obj, context, comptable=False)
                build_and_send_mail(context, None, obs)
                return context['state'], "closed", None
            elif accept == -1:
                return self.new(obj, -1, user)


    def closed(self, obj, accept=0, user=None):
        pass
