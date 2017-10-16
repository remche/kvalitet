# -*- coding: utf-8 -*-
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from compta.models import Service, Comptable, Directeur
from fchach.models import FchAch

@dajaxice_register
def update_next_user(request, service, fchach_id=None):
    dajax = Dajax()
    next_user = ""
    out = ""
    if service :
        if not fchach_id:
            next_user =  Service.objects.get(pk=service).tresorier
            if request.user == next_user:
                next_user = Comptable.objects.get(pk=1).comptable
                if request.user == next_user:
                    next_user = Directeur.objects.get(pk=1).directeur
        else:
            state = FchAch.objects.get(pk=fchach_id).state
            if state == 1:
                next_user = Comptable.objects.get(pk=1).comptable
                if request.user == next_user:
                    next_user = Directeur.objects.get(pk=1).directeur
            elif state == 2:
                next_user = Directeur.objects.get(pk=1).directeur

        if next_user:
            out = u"""<div class="span4 accordion-group" align="center">
                            <div class="accordion-heading">
                                <a class="accordion-toggle" data-toggle="collapse" href="#collapseMsg">
                                Écrire un message à %s %s</a>
                            </div>
                            <div id="collapseMsg" class="accordion-body collapse" style="height: Opx;">
                                <textarea class="input-xlarge textarea" name="message" cols="40" rows="5" id="id_message"></textarea>
                            </div>
                        </div>
                        """ % (next_user.first_name, next_user.last_name)

    dajax.assign('#message_div', 'innerHTML', out)
    return dajax.json()
