# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from compta.models import Entite, EntiteCat
import re

class Command(BaseCommand):
    args = '<fichier>'
    help = "Importe les entites du fichier passé en argument"

    def handle(self, *args, **options):
        if not args:
            print("Vous devez spécifier un fichier à importer")
        elif len(args) > 1:
            print("Vous ne pouvez spécifier qu'un seul fichier à importer")
        else:
            Entite.objects.all().update(active=False)
            EntiteCat.objects.all().update(active=False)
            try:
                categories = []
                entite=[]
                entite_autre=[]
                i=0
                f=open(args[0])
                f.next()
                for l in f:
                    m=re.search('\s{2}(?P<id>[&\w]*)\.{3,4}\t(?P<categorie>.*)', l.decode('latin1'))
                    if m:
                        categories+=[[(m.group('id'),m.group('categorie').split('\t')[0])]]
                        if entite:
                            categories[i-1] += [entite]
                        entite = []
                        i += 1
                    else:
                        n=re.search('\s{3}(?P<id>[-/\w\.]*)\t(?P<entite>.*)', l.decode('latin1'))
                        if n:
                            entite += [(n.group('id'),n.group('entite').split('\t')[0])]
                        else:
                            n=re.search('\s{2}(?P<id>[\w]*)\t(?P<entite>.*)', l.decode('latin1'))
                            entite_autre += [(n.group('id'),n.group('entite').split('\t')[0])]
                if entite:
                    categories[i-1] += [entite]
                if entite_autre:
                    categories += [[ ('AUTRE', 'Sans catégorie'), entite_autre ]]

                for cat in categories:
                    obj, created = EntiteCat.objects.get_or_create(numero=cat[0][0], nom=cat[0][1])
                    obj.active=True
                    obj.save()
                    for entite in cat[1]:
                        obj, created = Entite.objects.get_or_create(categorie=EntiteCat.objects.get(numero=cat[0][0]),
                                    numero=entite[0],
                                    nom=entite[1])
                        obj.active=True
                        obj.save()

            except Exception:
                print("Le fichier n'est pas au bon format")
