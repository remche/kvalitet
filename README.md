# Installation
## Dépendances

aptitude install \
subversion \
libjs-twitter-bootstrap libjs-jquery-ui libjs-jquery-ui-theme-smoothness \
django-ajax-selects \
python-django-celery \
python-redis redis-server \
python-pylibmc \
python-pip \
python-psycopg2 \
python-ldap python-django-auth-ldap \
python-twisted \
python-pisa \
 python-django-djapian
<notextile>#</notextile> (ou python-memcache, ms moins efficace) \
<notextile>#</notextile> python-django-debug-toolbar \
<notextile>#</notextile> python-django-extensions

aptitude install python-django-dajax python-django-dajaxice -t testing

pip install --upgrade django-crispy-forms


## Subversion

svn co https://forge.3sr-grenoble.fr/repos/kvalitet/trunk --username=rcailletaud

# Configuration

## pgsql

adduser kvalitet
createuser mypguser
createdb -O mypguser mypgdatabase


Optimizing PostgreSQL’s configuration (https://docs.djangoproject.com/en/dev/ref/databases/)
Django needs the following parameters for its database connections:
    client_encoding: 'UTF8',
    default_transaction_isolation: 'read committed',
    timezone: 'UTC' when USE_TZ is True, value of TIME_ZONE otherwise.

Configurer la base dans kvalitet/settings.py


## Dev

export DEVELOPMENT=1


## Static et import

(configurer base : south)
./manage.py syncdb
./manage.py migrate

./manage.py collectstatic

./manage.py importusers
./manage.py loaddata services tutelles direction
./manage.py loaddata batiments salles-e salles-i
./manage.py loaddata nomenclatures
./manage.py importxlab fichier_xlab.txt
./manage.py importentites fichier_entites.txt
./manage.py importfournisseurs fichier_fournisseurs.txt
./manage.py importlignes fichier_lignes.txt

## Redis

pour debug :
 ./manage.py celeryd -E -l INFO

## Gunicorn et Nginx

gunicron nginx supervisor
voir logrotate
TODO
