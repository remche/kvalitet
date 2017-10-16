# -*- coding: utf-8 -*-

import ldap
from django.contrib.auth.models import User, Group, Permission
from django.core.management.base import BaseCommand
from django.conf import settings

#à virer
#import sys

class Command(BaseCommand):
    help = "Importe utilisateurs et groupes du ldap"

    def handle(self, *args, **options):
        self.stdout.write("\n".join(self.sync_users())+"\n")
        self.stdout.write("\n".join(self.sync_groups())+"\n")
        self.stdout.write("\n".join(self.set_permissions())+"\n")

    def set_permissions(self):
        messages = []
        group_compta = Group.objects.get(name = "Groupe Utilisateurs Compta Qualite")
        permissions_compta = ["add_service", "change_service", "delete_service",\
                                "add_entite", "change_entite", "delete_entite",\
                                "add_fournisseur", "change_fournisseur", "delete_fournisseur",\
                                "add_ligne", "change_ligne", "delete_ligne",\
                                "add_nomenclature", "change_nomenclature", "delete_nomenclature",\
                                "add_matierexlab", "change_matierexlab", "delete_matierexlab"]
        for permission_compta in permissions_compta:
            group_compta.permissions.add(Permission.objects.get(codename=permission_compta))
        message =  "Permissions set"
        messages.append(message)
        return messages


    def get_ldap_groups(self):
        scope = settings.AUTH_LDAP_SCOPE
        filter = "(&(objectclass=group))"
        values = ['cn', 'member']
        l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(settings.AUTH_LDAP_BIND_DN,settings.AUTH_LDAP_BIND_PASSWORD)
        result_id = l.search('OU=Qualite,OU=Groupes,OU=Utilisateurs,'+settings.AUTH_LDAP_BASE, scope, filter, values)
        result_type, result_data = l.result(result_id, 1)
        l.unbind()
        return result_data

    def sync_groups(self):
        messages = []
        ldap_groups = self.get_ldap_groups()
        for ldap_group in ldap_groups:
            try: group_name = ldap_group[1]['cn'][0]
            except: pass
            else:
                try: group = Group.objects.get(name=group_name)
                except Group.DoesNotExist:
                    group = Group(name=group_name)
                    group.save()
                    message = "Group '%s' created." % group_name
                    messages.append(message)
        message = "Groups are synchronized."
        messages.append(message)
        return messages

    def get_ldap_users(self):
        scope = settings.AUTH_LDAP_SCOPE
        filter = "(&(objectclass=person))"
        values = ['uid', 'mail', 'givenName', 'sn', ]
        l = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(settings.AUTH_LDAP_BIND_DN,settings.AUTH_LDAP_BIND_PASSWORD)
        result_id = l.search('OU=Utilisateurs,'+settings.AUTH_LDAP_BASE, scope, filter, values)
        result_type, result_data = l.result(result_id, 1)
        l.unbind()
        return result_data

    def sync_users(self):
        messages = []
        ldap_users = self.get_ldap_users()
        ldap_groups = self.get_ldap_groups()
        for ldap_user in ldap_users:
            try: username = ldap_user[1]['uid'][0]
            except: pass
            else:
                try: email = ldap_user[1]['mail'][0]
                except: email = ''
                try: first_name = ldap_user[1]['givenName'][0]
                except: first_name = username
                try: last_name = ldap_user[1]['sn'][0]
                except: last_name = ''
                try: user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = User.objects.create_user(username, email, username)
                    user.first_name = first_name
                    user.last_name = last_name
                    message = "User '%s' created." % username
                    messages.append(message)
                else:
                    if not user.email == email:
                        user.email = email
                        message = "User '%s' email updated." % username
                        messages.append(message)
                    if not user.first_name == first_name:
                        user.first_name = first_name
                        message = "User '%s' first name updated." % username
                        messages.append(message)
                    if not user.last_name == last_name:
                        user.last_name = last_name
                        message = "User '%s' last name updated." % username
                        messages.append(message)
                user.save()
                for ldap_group in ldap_groups:
                    group_name = ldap_group[1]['cn'][0]
                    group_members = ldap_group[1]['member']
                    try:
                        group = Group.objects.get(name=group_name)
                    except:
                        pass
                    else:
                        if not user.username in group_members:
                            if group in user.groups.all():
                                user.groups.remove(group)
                                message = "User '%s' removed from group '%s'." % (user.username, group.name)
                                messages.append(message)
                        else:
                            if not group in user.groups.all():
                                user.groups.add(group)
                                message = "User '%s' added to group '%s'." % (user.username, group.name)
                                messages.append(message)
        message = "Users are synchronized."
        messages.append(message)
        return messages
