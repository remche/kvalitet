import ldap
from django_auth_ldap.config import LDAPSearch
from django_auth_ldap.config import ActiveDirectoryGroupType

AUTHENTICATION_BACKENDS = ('django_auth_ldap.backend.LDAPBackend',
                           'django.contrib.auth.backends.ModelBackend',)


AUTH_LDAP_SERVER = "ldap.domain.com"
AUTH_LDAP_SERVER_URI = "ldap://" +  AUTH_LDAP_SERVER
AUTH_LDAP_BIND_DN = "admin"
AUTH_LDAP_BIND_PASSWORD = "passwd"

AUTH_LDAP_SCOPE = ldap.SCOPE_SUBTREE
AUTH_LDAP_BASE = "dc=domain,dc=com"
AUTH_LDAP_USER_SEARCH = LDAPSearch('OU=Users,DC=domain,DC=com', AUTH_LDAP_SCOPE, "(uid=%(user)s)",)
AUTH_LDAP_GROUP_SEARCH = LDAPSearch('OU=Admin,OU=Groups,DC=domain,DC=com', AUTH_LDAP_SCOPE, "(objectClass=group)")
AUTH_LDAP_GROUP_TYPE = ActiveDirectoryGroupType()

AUTH_LDAP_USER_ATTR_MAP = {"first_name": "givenName", "last_name": "sn", "email" : "mail"}
#AUTH_LDAP_PROFILE_ATTR_MAP = {"home_directory": "homeDirectory"}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
        "is_staff": "CN=Compta,OU=Groups,OU=Users,DC=domain,DC=com",
}
#AUTH_LDAP_MIRROR_GROUPS=True
AUTH_LDAP_FIND_GROUP_PERMS=True
# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = False
#AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600
