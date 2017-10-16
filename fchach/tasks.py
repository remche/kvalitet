# -*- coding: utf-8 -*-
from celery.task import task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

@task
def send_mail(subject, html_content, text_content, from_email, dest):
    msg = EmailMultiAlternatives(subject, text_content, from_email, dest)
    msg.attach_alternative(html_content, "text/html")
    msg.send()



def build_and_send_mail(context, dest, obs):
    """
    (Tâche celery pour l'envoi d'email)
    Non asynchrone : bug dans django-celery avec ldap ?
    """
    # Mail pour le destinataire (prochain acteur)
    if dest :
        plaintext = get_template('fchach/mail/email-acteur.txt')
        htmly     = get_template('fchach/mail/email-acteur.html')

        subject, from_email = '[Qualité] Achat n°%s : action en attente de votre part' % context['fchach'].id, 'qualite@3sr-grenoble.fr'
        text_content = plaintext.render(context)
        html_content = htmly.render(context)
        send_mail.delay(subject, html_content, text_content, from_email, [dest.email])

    # Mails pour les observateurs
    for ob in obs:
        context['role'] = ob[0]
        plaintext = get_template('fchach/mail/email-obs.txt')
        htmly     = get_template('fchach/mail/email-obs.html')

        subject, from_email = '[Qualité] Achat n°%s: information - %s' \
                                % (context['fchach'].id, context['fchach'].workflow.states[context['state']][1]) , \
                            'qualite@3sr-grenoble.fr'
        text_content = plaintext.render(context)
        html_content = htmly.render(context)
        send_mail.delay(subject, html_content, text_content, from_email, [ob[1]])
