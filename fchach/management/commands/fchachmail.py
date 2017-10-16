# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.conf import settings
import re
from twisted.internet import reactor, protocol
from twisted.mail import imap4
from twisted.mail.imap4 import MessageSet
from twisted.internet import ssl
from email import message_from_string
from fchach.models import FchAch

"""
Commande pour retirer les mails workflow et les traiter
"""


USERNAME = 'qualite'
PASSWORD = 'Qu@L1t€'

contextFactory = ssl.ClientContextFactory()

def mailboxes(list):
    print list
    for flags,sep,mbox in list:
        print mbox

def loggedin(res, proto):
    d = proto.list('','*')
    d.addCallback(mailboxes)
    return d

def close(res, proto):
    d = proto.expunge()
    return d

def process_messages(res, proto):
    for message in res.values():
        mes = message_from_string(message['RFC822'])
        m = re.search('ACHSTATE:([0-9]+)\|ACHID:(\S{27}=)', message['RFC822'])
        if m:
            fch_tab = FchAch.objects.filter(cookie=m.group(2)).filter(state=m.group(1))
            if len(fch_tab) == 1:
                    if fch_tab[0].next_user.email in mes.get('From'):
                        fch_tab[0].version += 1
                        fch_tab[0].modified_by = fch_tab[0].next_user
                        fch_tab[0].message = ""
                        fch_tab[0].state, fch_tab[0].cookie, fch_tab[0].next_user = \
                                                                fch_tab[0].workflow.states[fch_tab[0].state][0](fch_tab[0], 1, fch_tab[0].next_user)
                        fch_tab[0].save()
    d = proto.setFlags(MessageSet(start=1,end=len(res)), ['\\Deleted'])
    d.addCallback(close, proto)
    return d


def fetch_messages(res, proto):
    d = proto.fetchMessage(MessageSet(start=1,end=res['MESSAGES']))
    d.addCallback(process_messages, proto)
    return d

def get_status(res, proto):
    if res['EXISTS']:
        d = proto.status('INBOX', 'MESSAGES')
        d.addCallback(fetch_messages, proto)
    else:
        d = proto.expunge()
    return d

def select_inbox(res, proto):
    d = proto.select("INBOX")
    d.addCallback(get_status, proto)
    return d

def connected(proto):
    d = proto.login(USERNAME, PASSWORD)
    d.addCallback(select_inbox, proto)
    d.addErrback(failed)
    return d

def failed(f):
    print "failed", f
    return f

def done(_):
    reactor.callLater(0, reactor.stop)

def main():
    c = protocol.ClientCreator(reactor, imap4.IMAP4Client)
    d = c.connectSSL(settings.EMAIL_HOST, settings.EMAIL_IMAP, contextFactory)
    d.addCallbacks(connected, failed)
    d.addBoth(done)

class Command(BaseCommand):
    help = "Check workflow mail"

    def handle(self, *args, **options):
        reactor.callLater(0, main)
        reactor.run()


