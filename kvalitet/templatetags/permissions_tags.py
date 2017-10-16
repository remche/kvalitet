from django import template
from kvalitet.abstract_models import FchQual

register = template.Library()

@register.filter
def can_edit(obj, user):
#    import ipdb; ipdb.set_trace()
    if isinstance(obj,FchQual):
        if obj.permissions.can_mod_line(obj,user, None) or \
            obj.permissions.can_edit(obj, user,None) or \
            obj.permissions.can_mod_emplacement(obj, user,None):
            return True
        if obj.next_user == user:
            return True
    return False
