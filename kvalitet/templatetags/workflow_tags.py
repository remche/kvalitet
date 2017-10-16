from django import template
from kvalitet.abstract_models import FchQual

register = template.Library()

@register.filter
def progress(object):
    if isinstance(object,FchQual) and object.workflow:
        if object.state == -1:
            return "100%"
        return str(int(float(object.state)/(len(object.workflow.states)-1)*100))+"%"
    return ""

@register.filter
def state_str(object, arg=None):
    if isinstance(object,FchQual) and object.workflow:
        if arg:
            return object.workflow.states[arg][1]
        else:
            return object.workflow.states[object.state][1]
