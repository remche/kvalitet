# -*- coding: utf-8 -*-
from django import forms
from django.forms.fields import ChoiceField
from django.forms import ModelChoiceField
from django.forms.widgets import RadioSelect
from django.contrib.auth.models import User
from ajax_select import make_ajax_field
from kvalitet.multifile import MultiFileField
from fchach.prodfield import ProdField, ProdWidget
from kvalitet.forms import UserChoiceField
from fchach.models import FchAch, FchAchDoc, FchAchProd
from compta.models import Batiment, Entite, EntiteCat, Ligne, Tutelle
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit, Reset, HTML
#from crispy_forms.layout import Submit

class FchAchForm(forms.ModelForm):
    """
    Class Form pour les fiches achats
    """
    fichiers = MultiFileField(required=False)
    produits = ProdField(widget=ProdWidget(), required=False)
    client = UserChoiceField(queryset=User.objects.all().order_by('last_name'))
    batiment = ModelChoiceField(queryset=Batiment.objects.all().order_by('nom'))
    fournisseur = make_ajax_field(FchAch,'fournisseur','fournisseur',help_text="Tapez du texte pour chercher un fournisseur")
    entite = ModelChoiceField(queryset=Entite.objects.filter(active=True))
    ligne = ModelChoiceField(queryset=Ligne.objects.filter(active=True), required=False)
    #TODO : le mettre plutôt dans models ? (pb de référence cicrulaire...)
    documents = FchAchDoc

    class Meta:
        model = FchAch
        fields = ('titre', 'client', 'team', 'entite', 'ligne', 'fournisseur', 'comments', 'fichiers', 'emplacement', 'message')

    def build_choices(self, obj, cat, cat_order, cat_key, filter_service=None):
        choices_opt = [ ["", "---------"] ]
        for cat in  cat.objects.filter(active=True).order_by(cat_order):
            new_cat = []
            sub_cat = []
            if filter_service:
                d={ cat_key: cat, 'service': filter_service, 'active': True}
            else:
                d={ cat_key: cat, 'active': True }
            for opt in obj.objects.filter(**d).order_by('numero'):
                sub_cat.append([opt.id, opt.__unicode__()])
            if sub_cat:
                new_cat = [cat.__unicode__(), sub_cat]
                choices_opt.append(new_cat)
        return choices_opt

    def __init__(self, *args, **kwargs):
        super(FchAchForm, self).__init__(*args, **kwargs)
        self.base_fields['entite'].choices = self.build_choices(Entite, EntiteCat, "numero", "categorie")
        self.base_fields['ligne'].choices = self.build_choices(Ligne, Tutelle, "nom", "tutelle")
        self.fields['ligne'].required = False
        self.helper = FormHelper()
        self.helper.form_class = "well form-inline"
        self.helper.form_id = "fchach_form"
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.layout = Layout(Div(Div('titre', css_class='span8 pagination-centered'), css_class="row"),
                                        Div(
                                            Div('client', css_class='span4 pagination-centered'),
                                            Div('team', css_class='span4 pagination-centered'),
                                            css_class="row"),
                                        Div(
                                            Div('ligne', css_class='span4 pagination-centered'),
                                            Div('entite', css_class='span4 pagination-centered'),
                                            css_class="row"),
                                        Div(
                                            Div('fournisseur', css_class='span4 pagination-centered'),
                                            Div(Field('message', type='hidden', css_class='span4 pagination-centered'),
                                                id='message_div', css_class='span4 pagination-centered'),
                                            css_class="row"),
                                        Div(
                                            Div('batiment', css_class='span4 pagination-centered'),
                                            Div('emplacement', css_class='span4 pagination-centered'),
                                            css_class="row"),
                                        Div(
                                            Div(
                                                HTML(u"""<div class="span8 accordion-group" align="center">
                                                            <div class="accordion-heading">
                                                                <a class="accordion-toggle" data-toggle="collapse" href="#collapsePlans">
                                                                    <b class="caret pull-left"></b>
                                                                    Plans<b class="caret pull-right"></b>
                                                                </a>
                                                            </div>
                                                            <div id="collapsePlans" class="accordion-body collapse" style="height: Opx;">
                                                                <table class="table">
                                                                <tr><td><a href="/static/img/bate0.png" target="_blank">Batiment E - RDC </a></td>
                                                                    <td><a href="/static/img/bate1.png" target="_blank">Batiment E - 1er étage</a></td></tr>
                                                                <tr><td><a href="/static/img/bati0.png" target="_blank">Batiment I - RDC </a></td>
                                                                    <td><a href="/static/img/bati1.png" target="_blank">Batiment I - 1er étage</a><br></td></tr>
                                                                </table>
                                                            </div>
                                                        </div>
                                                        """),
                                                css_class="span8 pagination-centered"),
                                            css_class="row"),
                                        Div(
                                            Div(Field('produits', css_class="span8"), css_class="span8 scrollable", align="center"),
                                            css_class="row"),
                                        Div(
                                            Div(Field('comments', rows="3", css_class="input-xlarge"), css_class='span4 pagination-centered'),
                                            Div('fichiers', css_class="span4 pagination-centered"),
                                            css_class="row"),
                                   )
        if self.instance:
            self.fields['produits'].initial=list(FchAchProd.objects.filter(fchach=self.instance))
            self.fields['fichiers'].initial=list(FchAchDoc.objects.filter(fchqual=self.instance))

class FchAchCreateForm(FchAchForm):
    def __init__(self, *args, **kwargs):
        super(FchAchCreateForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(self.helper.layout,
                                    Div(
                                       Div(Submit("submit", "Soumettre la fiche"), Reset("reset", "Annuler"), css_class="span8 pagination-centered"),
                                    css_class="row"),
                                        HTML(u"""
                                            <div id="noprod" class="modal hide fade alert-error" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
                                                <div class="modal-header">
                                                    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                                                    <h3 id="myModalLabel">Erreur !</h3>
                                                </div>
                                                <div class="modal-body">
                                                    <p><i class="icon-warning-sign"></i> Vous n'avez aucun produit dans votre panier, pour les y ajouter, appuyez sur <i class="icon-plus"></i>.</p>
                                                </div>
                                                <div class="modal-footer">
                                                    <button class="btn" data-dismiss="modal" aria-hidden="true">Fermer</button>
                                                </div>
                                            </div>
                                        """),
                                        HTML(u"""
                                            <div id="prodleft" class="modal hide fade alert" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
                                                <div class="modal-header">
                                                    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
                                                    <h3 id="myModalLabel">Attention !</h3>
                                                </div>
                                                <div class="modal-body">
                                                    <p><i class="icon-warning-sign"></i>Vous n'avez pas ajouté ce produit : <strong id="forgotten"></strong><br/>
                                                        Êtes vous sûrs de vouloir valider la fiche ?</p>
                                                </div>
                                                <div class="modal-footer">
                                                    <button id="prodleft-validate-btn" class="btn btn-primary" >Valider</button>
                                                    <button class="btn btn-inverse" data-dismiss="modal" aria-hidden="true">Annuler</button>
                                                </div>
                                            </div>
                                        """),
                                   )

class FchAchUpdateForm(FchAchForm):
    accept = ChoiceField(required=True, widget=RadioSelect, choices=((1, "Accepter "), (-1, "Refuser")), label="")
    def __init__(self, *args, **kwargs):
        super(FchAchUpdateForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(self.helper.layout,
                                        Div(
                                            Div(
                                                Field('accept', template="../templates/fchach/crispy-accept.html", css_class="span8"),
                                                css_class="span8 alert alert-info pagination-centered"),
                                            Submit("submit", "Valider"), HTML('<a href="{{ fchach_url }}" class="btn btn-danger"> Annuler </a>'),
                                        css_class="row")
                                   )

class FchAchValidateForm(FchAchUpdateForm):
    """
    Class Form pour les fiches achats - read only - seulement validation et commentaires
    """

    def __init__(self, *args, **kwargs):
        super(FchAchValidateForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.id:
            self.fields['titre'].widget.attrs['readonly'] = True
            readonly_selects = ['client', 'team', 'entite', 'ligne', 'fournisseur', 'batiment', 'emplacement']
            self.data.update({ 'client': self.instance.client.id, 'team': self.instance.team.id,
                                'entite': self.instance.entite.id, 'ligne': self.instance.ligne.id,
                                'fournisseur': self.instance.fournisseur.id, 'batiment':self.instance.emplacement.batiment.id,
                                'emplacement': self.instance.emplacement.id})
            for readonly in readonly_selects:
                self.fields[readonly].widget.attrs['disabled'] = True
        if self.instance:
            self.fields['batiment'].initial=self.instance.emplacement.batiment.id
            self.fields['produits'].initial=list(FchAchProd.objects.filter(fchach=self.instance))
            self.fields['produits'].widget.attrs['disabled'] = True
            self.fields['fichiers'].initial=list(FchAchDoc.objects.filter(fchqual=self.instance))


class FchAchLineForm(FchAchUpdateForm):
    """
    Class Form pour les fiches achats - read only - seulement validation et commentaires + ligne
    """

    def __init__(self, *args, **kwargs):
        super(FchAchLineForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.id:
            self.fields['titre'].widget.attrs['readonly'] = True

            self.data.update({ 'client': self.instance.client.id, 'team': self.instance.team.id,
                                'entite': self.instance.entite.id, 'fournisseur': self.instance.fournisseur.id,
                                'batiment':self.instance.emplacement.batiment.id, 'emplacement': self.instance.emplacement.id})
            if self.instance.ligne:
                self.data.update({ 'ligne': self.instance.ligne.id })
            else:
                self.fields['ligne'].choices = self.build_choices(Ligne, Tutelle, "nom", "tutelle", filter_service=self.instance.team.id)

            readonly_selects = ['client', 'team', 'fournisseur', 'entite', 'batiment', 'emplacement']
            for readonly in readonly_selects:
                self.fields[readonly].widget.attrs['disabled'] = True
            self.fields['ligne'].required = True

        if self.instance:
            self.fields['batiment'].initial=self.instance.emplacement.batiment.id
            self.fields['produits'].initial=list(FchAchProd.objects.filter(fchach=self.instance))
            self.fields['produits'].widget.attrs['disabled'] = True
            self.fields['fichiers'].initial=list(FchAchDoc.objects.filter(fchqual=self.instance))


class FchAchEmplacementForm(FchAchForm):
    """
    Class Form pour les fiches achats - read only - seulement validation et commentaires + ligne
    """

    def __init__(self, *args, **kwargs):
        super(FchAchEmplacementForm, self).__init__(*args, **kwargs)

        self.helper.layout = Layout(self.helper.layout,
                                        Submit("submit", "Valider"), HTML('<a href="{{ fchach_url }}" class="btn btn-danger"> Annuler </a>')
                                   )

        if self.instance and self.instance.id:
            self.fields['titre'].widget.attrs['readonly'] = True

            self.data.update({ 'client': self.instance.client.id, 'team': self.instance.team.id,
                                'entite': self.instance.entite.id, 'fournisseur': self.instance.fournisseur.id })

            readonly_selects = ['client', 'team', 'fournisseur', 'ligne', 'entite']
            for readonly in readonly_selects:
                self.fields[readonly].widget.attrs['disabled'] = True
            self.fields['ligne'].required = True

        if self.instance:
            self.fields['batiment'].initial=self.instance.emplacement.batiment.id
            self.fields['produits'].initial=list(FchAchProd.objects.filter(fchach=self.instance))
            self.fields['produits'].widget.attrs['disabled'] = True
            self.fields['fichiers'].initial=list(FchAchDoc.objects.filter(fchqual=self.instance))
