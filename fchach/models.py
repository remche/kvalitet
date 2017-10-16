# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from kvalitet.abstract_models import FchQual, FchQualHistory, FchQualDoc
from fchach.workflow import FchAchWorkflow
from fchach.permissions import FchAchPerms
from compta.models import Ligne, Nomenclature, MatiereXlab, Fournisseur, Entite, Salle


class AbstractFchAch(FchQual):
    """
    Classe abstraite pour les fiches achat
    """
    titre = models.CharField(max_length=200)
    emplacement = models.ForeignKey(Salle, verbose_name="Salle")
    client = models.ForeignKey(User)
    entite = models.ForeignKey(Entite)
    ligne = models.ForeignKey(Ligne, blank=True, null=True)
    fournisseur = models.ForeignKey(Fournisseur)
    permissions = FchAchPerms()
    workflow = FchAchWorkflow()

    class Meta:
        abstract = True


class FchAch(AbstractFchAch):
    """
    Classe pour les fiches achat
    """
    context_string = "fchach"

    def __unicode__(self):
        return "Fiche achat " + str(self.id)

class FchAchHistory(AbstractFchAch, FchQualHistory):
    """
    Classe pour l'historique des fiches achats
    """
    fchqual = models.ForeignKey(FchAch, related_name="%(app_label)s_%(class)s_fchqual_related")

    def __unicode__(self):
        return "Fiche achat " + str(self.fchqual) + " version " + str(self.version)

class FchAchProd(models.Model):
    fchach = models.ForeignKey(FchAch)
    produit = models.CharField(max_length=200)
    prixht = models.DecimalField(verbose_name="Prix HT", max_digits=9, decimal_places=2)
    quantite = models.IntegerField(verbose_name="Quantité")
    nomenclature = models.ForeignKey(Nomenclature)
    matiere_xlab = models.ForeignKey(MatiereXlab)

    def total(self):
        return self.prixht * self.quantite

class FchAchDoc(FchQualDoc):
    fchqual = models.ForeignKey(FchAch)

    def __init__(self, *args, **kwargs):
        super(FchQualDoc, self).__init__(*args, **kwargs)
        self.doc_type = "achats"
