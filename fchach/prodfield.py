# -*- coding: utf-8 -*-
"""
A newforms widget and field to allow multiple file uploads.

Created by Edward Dale (www.scompt.com)
Modified by Rémi Cailletaud
Released into the Public Domain
"""

from django.forms.fields import Field
from django.db import models
from django.forms.widgets import Widget
from django.forms.util import ValidationError
from compta.models import Nomenclature, NomenclatureCat, MatiereXlab, MatiereXlabCat

def clean_data(data):
    data_cleaned = {}
    for k in data.items():
        if k[0].partition("-")[2] not in data_cleaned:
            data_cleaned[k[0].partition("-")[2]] = dict()
        data_cleaned[k[0].partition("-")[2]][k[0].partition("-")[0]] = k[1][0]
    return data_cleaned


class ProdWidget(Widget):
    """
    Widget pour la liste de produits
    """

    def __init__(self, attrs=None):
        self.nomenclatures=Nomenclature.objects.all().order_by('nom')
        super(ProdWidget, self).__init__(attrs)


    def render_mat_opt(self, selected=None):
        opt_str = "<option id='mat_opt' class='mat_opt' value=''>---------</option>"
        xlab_categories = MatiereXlabCat.objects.all().order_by('numero')
        for xlab_cat in xlab_categories:
            opt_str += "<optgroup label='%(categorie)s'>" % { 'categorie': xlab_cat }
            matieres = MatiereXlab.objects.filter(categorie=xlab_cat).order_by('numero')
            for matiere in matieres:
                if selected and selected == matiere.id:
                    opt_str += u"<option id='mat_opt' class='mat_opt' value='%(id)s' selected=selected>%(matiere)s<option>" \
                                    % { 'id': matiere.id, 'matiere': matiere }
                else:
                    opt_str += u"<option id='mat_opt' class='mat_opt' value='%(id)s'>%(matiere)s</option>" \
                                    % { 'id': matiere.id, 'matiere': matiere }
        return opt_str

    def render_nom_opt(self, selected=None):
        opt_str = "<option id='nom_opt' class='nom_opt' value=''>---------</option>"
        nom_categories = NomenclatureCat.objects.all().order_by('numero')
        for nom_cat in nom_categories:
            opt_str += "<optgroup label='%(categorie)s'>" % { 'categorie': nom_cat }
            nomenclatures = Nomenclature.objects.filter(categorie=nom_cat).order_by('numero')
            for nomenclature in nomenclatures:
                if selected and selected == nomenclature.id:
                    opt_str += u"<option id='nom_opt' class='nom_opt' value='%(id)s' selected=selected>%(nomenclature)s<option>" \
                                    % { 'id': nomenclature.id, 'nomenclature': nomenclature }
                else:
                    opt_str += u"<option id='nom_opt' class='nom_opt' value='%(id)s'>%(nomenclature)s</option>" \
                                    % { 'id': nomenclature.id, 'nomenclature': nomenclature }
        return opt_str


    def render(self, name, value, attrs=None):
        """
        Renders the ProdWidget
        Should not be overridden.  Instead, subclasses should override the
        js, link, and/or fields methods which provide content to this method.
        """
        final_attrs = self.build_attrs(attrs, type='text', name=name+'[]')
        if 'disabled' not in final_attrs:
            final_attrs['disabled'] = False
        js = self.js(name, value, final_attrs)
        fields = self.fields(name, value, final_attrs)

        return js+fields


    def add_row(self, num, intitule, matiere, nomenclature, prix, quantite, disabled):
        """
        Recharge une ligne de la table produits
        """
        row = u"""<tr id=prod%(num)s>
                    <td><input id="intitule-%(num)s" class="intitule" type="text" name="intitule-%(num)s" readonly="readonly" value="%(produit)s"></td>
                    <td><select class="matiere input-small" id="matiere-%(num)s" disabled="disabled">%(mat_options)s</select>
                        <input type="hidden" name="matiere-%(num)s" value="%(mat_id)s" /></td>
                    <td><select class="nomenclature input-small" id="nomenclature-%(num)s" disabled="disabled">%(nom_options)s</select>
                        <input type="hidden" name="nomenclature-%(num)s" value="%(nom_id)s" /></td>
                    <td><input id="prix-%(num)s" class="prix input-mini" type="text" name="prix-%(num)s" readonly="readonly"  value="%(prixht)s"></td>
                    <td><input id="quantite-%(num)s" class="qte input-mini" type="text" name="quantite-%(num)s" readonly="readonly"  value="%(quantite)s"></td>
                    <td><input id="sstotal" class="sstotal input-mini" type="text" readonly="readonly" value="%(sstotal)s">
                    </td>""" % {'num': num, 'produit': intitule,
                                'mat_options': self.render_mat_opt(matiere), 'mat_id': matiere,
                                'nom_options': self.render_nom_opt(nomenclature), 'nom_id': nomenclature,
                                'prixht': str(prix).replace('.',','),
                                'quantite': quantite, 'sstotal': str(prix*quantite).replace('.',',') }

        if not disabled :
            row += """<td>
                    <a id="suppr-%(num)s" class="suppr"><i class=icon-minus></i></a>
                    </td>"""

        return row + """</tr>"""

    def fields(self, name, value, attrs=None):
        """
        Renders the necessary number of input boxes.
        """
        table = u"""
                        <table  class="table-bordered table-striped table-condensed responsive span8" id="produits">
                        <thead>
                        <tr><th>Intitulé</th><th id="mat_xlab" >Matière XLAB</th><th id="nomenclature">Nomenclature</th><th>Prix</th><th>Quantit&eacute;</th><th>Sous-total</th></tr>
                        </thead>
                        <tbody>
                        """

        if not attrs['disabled']:
            table += u"""<tr id="prod_add">
                         <td><input class="intitule input-normal" id="intitule"  type="text"/></td>
                         <td><select class="matiere input-small" id="matiere">%(mat_options)s</select></td>
                         <td><select class="nomenclature input-small" id="nomenclature">%(nom_options)s</select></td>
                         <td><input class="prix input-mini" id="prix"  type="text"/></td>
                         <td><input class="qte input-mini" id="quantite" value="1" type="text"/></td>
                         <td><input class="sstotal input-mini" id="sstotal" readonly="readonly" value="0"  type="text"/></td>
                         <td><a id="add_button"><i class="icon-plus"></i></a></td></tr>
                         <tr><td colspan="5">Cliquez sur <i class="icon-plus"></i> pour ajouter les produits au panier </td>
                         </tr> """ % {'mat_options': self.render_mat_opt(), 'nom_options': self.render_nom_opt()}

        if isinstance(value,list):
            for val in value:
               table += self.add_row(value.index(val)+1, val.produit, val.matiere_xlab.id, val.nomenclature.id, val.prixht, val.quantite, attrs['disabled'])
        if isinstance(value,dict):
            # si recharge après erreur de formulaire
            #import ipdb; ipdb.set_trace()
            for val in clean_data(value).values():
               table += self.add_row(clean_data(value).values().index(val)+1, val['intitule'], int(val['matiere']), int(val['nomenclature']), \
                                        float(val['prix'].replace(',','.')), int(val['quantite']), attrs['disabled'])
        table += '''
                    <tr id="total_line"><td colspan="5"><strong>Total:</strong></td><td><input id="total" class="input-mini" readonly="readonly"/></td></tr>
                     </tbody></table>
                '''
        return table

    def js(self, name, value, attrs=None):
        """
        Javascript qui va bien.
        """
        if attrs['disabled']:
            return ''
        else:
            return u'''
        <script type="text/javascript" src="/static/js/prodfield.js"></script>
        <script type="text/javascript">window.onload=function(){ i=%(num)s; recal_total(); }</script>
        ''' % {'num': len(value)+1 }

    def value_from_datadict(self, data, files, name):
        """
        On récupère les valeurs pour les champs produits
        """
        my_data = {}
        for d in data.lists():
            if d[0].startswith('prix') or d[0].startswith('quantite') or d[0].startswith('intitule') or \
                    d[0].startswith('matiere') or  d[0].startswith('nomenclature'):
                my_data[d[0]] = d[1]
        return my_data

class ProdField(Field):
    """
    Field pour les produits
    """
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.widget = kwargs['widget']
        super(ProdField, self).__init__(*args, **kwargs)

    def clean(self, data):
        """
        Vérifie qu'on a au moins un produit, lève une exception sinon
        Trie les produits par leur "id" dans la fiche
        """
        super(ProdField, self).clean(data)
        if not data:
            raise ValidationError(u"Vous n'avez précisé aucun produit !")
        else:
            return clean_data(data)
