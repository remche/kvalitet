# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from compta.models import Ligne, Service, Tutelle

class Command(BaseCommand):
    args = '<fichier>'
    help = "Importe les lignes du fichier passé en argument"

    def handle(self, *args, **options):
        if not args:
            print("Vous devez spécifier un fichier à importer")
        elif len(args) > 1:
            print("Vous ne pouvez spécifier qu'un seul fichier à importer")
        else:
            Ligne.objects.all().update(active=False)
            try:
                for i in open(args[0]):
                    if not i.startswith("#"):
                        csv_ligne = i.split('\t')
                        try :
                            obj = Ligne.objects.get(numero=csv_ligne[0])
                            obj.nom = csv_ligne[1]
                            obj.service = Service.objects.get(pk=csv_ligne[2])
                            obj.reponsable = User.objects.get(username=csv_ligne[3])
                            obj.tutelle = Tutelle.objects.get(pk=csv_ligne[4])
                            obj.active=True
                        except Ligne.DoesNotExist:
                            obj = Ligne(numero=csv_ligne[0], nom=csv_ligne[1], service=Service.objects.get(pk=csv_ligne[2]),
                                            responsable=User.objects.get(username=csv_ligne[3]), tutelle=Tutelle.objects.get(pk=csv_ligne[4]))
                        obj.save()
            except Exception:
                print("Le fichier n'est pas au bon format")
