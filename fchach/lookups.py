from ajax_select import LookupChannel
from django.utils.html import escape
from django.db.models import Q
from compta.models import Fournisseur
from django.core.exceptions import PermissionDenied

class FournisseurLookup(LookupChannel):

    model = Fournisseur
    min_length = 3
    plugin_options = {
        "minLength": min_length,
    }

    def get_query(self,q,request):
        return Fournisseur.objects.filter(Q(nom__icontains=q)).order_by('nom')

    def get_result(self,obj):
        u""" result is the simple text that is the completion of what the person typed """
        return obj.nom

    def format_match(self,obj):
        """ (HTML) formatted item for display in the dropdown """
        return self.format_item_display(obj)

    def format_item_display(self,obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return u"%s<div><i>%s</i></div>" % (escape(obj.nom),escape(obj.siret))

    def check_auth(self,request):
        if not request.user.is_authenticated:
            raise PermissionDenied
