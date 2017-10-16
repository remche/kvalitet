# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class ComptaModel(models.Model):
    nom = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.nom

    class Meta:
        abstract = True

class ComptaNumeroModel(ComptaModel):
    numero = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.numero + " - " + self.nom

    class Meta:
        abstract = True


class Directeur(models.Model):
    directeur = models.ForeignKey(User)

class DirecteurAdj(models.Model):
    directeur_adj = models.ForeignKey(User)

class Comptable(models.Model):
    comptable = models.ForeignKey(User)

class Service(ComptaModel):
    """
    Classe pour les "services" (équipes)
    """
    chef = models.ForeignKey(User, related_name="service_chef")
    tresorier = models.ForeignKey(User, related_name="service_tresorier")
    secretaire = models.ForeignKey(User, related_name="service_secretaire")

class Tutelle(ComptaModel):
    """
    Classe pour les tutelles (INP, UJF, CNRS, etc...)
    """
    pass

class EntiteCat(ComptaNumeroModel):
    """
    Classe pour les entités depensières (projets)
    """
    pass

class Entite(ComptaNumeroModel):
    """
    Classe pour les entités depensières (projets)
    """
    categorie = models.ForeignKey(EntiteCat)

class Ligne(ComptaNumeroModel):
    """
    Classe pour les lignes budgétaires
    """
    service = models.ForeignKey(Service, related_name="ligne_service")
    responsable = models.ForeignKey(User, related_name="ligne_responsable")
    tutelle = models.ForeignKey(Tutelle, related_name="ligne_tutelle")

class NomenclatureCat(ComptaNumeroModel):
    """
    Classe pour les catégories de nomenclature
    """
    pass

class Nomenclature(ComptaNumeroModel):
    """
    Classe pour les nomenclatures
    """
    categorie = models.ForeignKey(NomenclatureCat)

class MatiereXlabCat(ComptaNumeroModel):
    """
    Classe pour les catégories de matières xlab
    """
    pass


class MatiereXlab(ComptaNumeroModel):
    """
    Classe pour les matières XLAB
    """
    categorie = models.ForeignKey(MatiereXlabCat)

class Fournisseur(ComptaModel):
    """
    Classe pour les fournisseurs
    """
    siret = models.CharField(max_length=20, blank=True)

class Batiment(ComptaModel):
    """
    Classe pour les bâtiments
    """

class Salle(ComptaModel):
    """
    Classe pour les salles
    """
    batiment = models.ForeignKey(Batiment)

