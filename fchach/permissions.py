# -*- coding: utf-8 -*-
from kvalitet.abstract_models import FchQualPerms

class FchAchPerms(FchQualPerms):
    """
    Classe pour la gestion des permissions
    Implémente can_view et can_edit
    """

    def can_view(self, obj, user, roles):
        """
        L'utilisateur peut voir ses fiches
        Le trésorier et les chefs d'équipes peuvent voir les fiches de leurs équipes
        """
        if obj.created_by == user or obj.client == user:
            return True
        if roles:
            if roles['directeur'] or roles['comptable'] or \
            obj.team in roles['tresorier'] or obj.team in roles['chef'] or \
            obj.ligne in roles['resp_ligne']:
                return True
        return False

    def can_validate(self, obj, user, roles):
        if roles:
            if roles['comptable'] and (obj.state == 2 or obj.state == 4):
                return True
            elif roles['directeur'] and obj.state == 3:
                return True
        return False

    def can_mod_line(self, obj, user, roles):
        if roles:
            if obj.team in roles['tresorier'] and obj.state == 1:
                return True
        return False

    def can_mod_emplacement(self, obj, user, roles):
        if obj.created_by == user and (obj.state == 0 or obj.state == 1):
            return True
        elif obj.client == user and obj.state == -1:
            return True
        return False

    def can_edit(self, obj, user, roles):
        """
        L'utilisateur peut éditer la fiche tant qu'elle est en étape 0
        """
        if obj.created_by == user and (obj.state == 1 or obj.state == 0):
            return True
        return False
