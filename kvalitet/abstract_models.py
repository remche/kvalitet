# -*- coding: utf-8 -*-
from django.db import models
from compta.models import Service
from django.contrib.auth.models import User
import os, time

class FchQual(models.Model):
    """
    Classe abstraite pour toutes les fiches qualités
    """
    created_by = models.ForeignKey(
        User, related_name="%(app_label)s_%(class)s_createdby_related",
        verbose_name="Créée par")

    modified_by = models.ForeignKey(
        User, related_name="%(app_label)s_%(class)s_modifiedby_related",
        verbose_name="Modifiée par")

    creation_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de création",
        verbose_name="Date de création")

    modification_date = models.DateTimeField(
        auto_now_add=True,
        auto_now=True,
        help_text="Date de dernière modification",
        verbose_name="Date de modification")

    team = models.ForeignKey(Service,
                            verbose_name="Équipe")
    state = models.IntegerField(default=0)
    version = models.IntegerField(default=0)
    comments = models.TextField(verbose_name="Commentaires", default="", blank=True)
    cookie = models.CharField(max_length=30)
    next_user = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_nextuser_related", blank=True, null=True)
    message = models.TextField(verbose_name="Message", default="", blank=True)

    class Meta:
        abstract = True

class FchQualHistory:
    """"
    Classe pour l'historique. Permet de faire des vérification en fonction du type.
    """
    def is_history(self):
        """
        Utilisé uniquement dans les templates
        """
        return True


    class Meta:
        abstract = True


def upload_to(instance, filename):
    """
    Fonction pour générer le path d'upload des fichiers
    """
    return '/'.join(['doc', instance.doc_type, time.strftime('%Y'), str(instance.fchqual.id), filename])

class FchQualDoc(models.Model):
    user = models.ForeignKey(User, help_text="Créée par", verbose_name="Créée par")
    doc = models.FileField(upload_to=upload_to)

    def filename(self):
        return os.path.basename(self.doc.name)

    def delete(self, *args, **kwargs):
        """
        Pour effacer le fichier (django ne le fait pas automatiquement)
        """
        storage, path = self.doc.storage, self.doc.path
        super(FchQualDoc, self).delete(*args, **kwargs)
        storage.delete(path)

    class Meta:
        abstract = True

class FchQualPerms:
    def can_view(self, obj, user, roles):
        pass
    def can_edit(self, obj, user, roles):
        pass
