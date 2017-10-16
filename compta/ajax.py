# -*- coding: utf-8 -*-
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from compta.models import Salle, Ligne, Tutelle

@dajaxice_register
def update_ligne(request, service):
    dajax = Dajax()
    out = ["<option>---------</option>"]
    for tutelle in Tutelle.objects.all().order_by('nom'):
        if service :
            lignes = Ligne.objects.filter(service=service, tutelle=tutelle, active=True).order_by('numero')
        else:
            lignes = Ligne.objects.filter(tutelle=tutelle, active=True).order_by('numero')
        if lignes:
            out.append("<optgroup label='%s'>" % (tutelle))
            for option in lignes:
                out.append("\t<option value='%s'>%s</option>\n" % (option.id, option))
            out.append("</optgroup>\n")

    dajax.assign('#id_ligne', 'innerHTML', ''.join(out))
    return dajax.json()


@dajaxice_register
def update_salle(request, bat):
    dajax = Dajax()
    if bat :
        salles = Salle.objects.filter(batiment=bat).order_by('nom')
    else:
        salles = Salle.objects.all().order_by('nom')

    out = ["<option>---------</option>"]
    for option in salles:
        out.append("<option value='%s'>%s</option>" % (option.id, option))

    dajax.assign('#id_emplacement', 'innerHTML', ''.join(out))
    return dajax.json()
