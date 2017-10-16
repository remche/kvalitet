# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from compta.models import Fournisseur

class Command(BaseCommand):
    args = '<fichier>'
    help = "Importe les fournisseurs du fichier passé en argument"

    def handle(self, *args, **options):
        if not args:
            print("Vous devez spécifier un fichier à importer")
        elif len(args) > 1:
            print("Vous ne pouvez spécifier qu'un seul fichier à importer")
        else:
            Fournisseur.objects.all().update(active=False)
            try:
                for line in open(args[0]):
                    obj, created = Fournisseur.objects.get_or_create(nom=line.split('\t')[1].decode('latin1'),
                                                                    siret=line.split('\t')[3].decode('latin1'))
                    obj.active=True
                    obj.save()
            except Exception:
                print("Le fichier n'est pas au bon format")

