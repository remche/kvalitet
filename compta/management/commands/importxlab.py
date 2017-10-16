# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from compta.models import MatiereXlab, MatiereXlabCat
import re

class Command(BaseCommand):
    args = '<fichier>'
    help = "Importe les matières xlab du fichier passé en argument"

    def handle(self, *args, **options):
        if not args:
            print("Vous devez spécifier un fichier à importer")
        elif len(args) > 1:
            print("Vous ne pouvez spécifier qu'un seul fichier à importer")
        else:
            MatiereXlab.objects.all().update(active=False)
            MatiereXlabCat.objects.all().update(active=False)
            try:
                categories = []
                xlab=[]
                i=0
                for l in open(args[0]):
                    m=re.search('\s*(?P<id>[\w])\.\.\.\t(?P<categorie>[\w\s]*)\n', l.decode('latin1'))
                    if m:
                        categories+=[[(m.group('id'),m.group('categorie'))]]
                        if xlab:
                            categories[i-1] += [xlab]
                        xlab = []
                        i += 1
                    else:
                        n=re.search('\s*(?P<id>[\w]*)\t(?P<xlab>.*)\n', l.decode('latin1'))
                        if n:
                            xlab += [(n.group('id'),n.group('xlab'))]
                if xlab:
                    categories[i-1] += [xlab]

                for cat in categories:
                    obj, created = MatiereXlabCat.objects.get_or_create(numero=cat[0][0], nom=cat[0][1])
                    obj.active=True
                    obj.save()

                    for xlab_mat in cat[1]:
                        obj, created = MatiereXlab.objects.get_or_create(categorie=MatiereXlabCat.objects.get(numero=cat[0][0]),
                                    numero=xlab_mat[0], nom=xlab_mat[1])
                        obj.active=True
                        obj.save()
            except Exception:
                print("Le fichier n'est pas au bon format")
