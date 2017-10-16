from django import template
from django.db.models.query import QuerySet
from fchach.models import FchAchProd

register = template.Library()

@register.filter
def total(object):
    total = 0
    if isinstance(object, QuerySet) and isinstance(object[0], FchAchProd):
        for prod in object:
            total += prod.total()
        return total


