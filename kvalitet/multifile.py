# -*- coding: utf-8 -*-
"""
A newforms widget and field to allow multiple file uploads.

Created by Edward Dale (www.scompt.com)
Modified by Rémi Cailletaud
Released into the Public Domain
"""

from django.utils.datastructures import MultiValueDict
from django.utils.translation import ugettext
from django.forms.fields import Field, EMPTY_VALUES
from django.core.files.uploadedfile import UploadedFile
from django.forms.widgets import FileInput
from django.forms.util import ValidationError, flatatt
from django.template import defaultfilters
from django.core.files.uploadedfile import InMemoryUploadedFile

class MultiFileInput(FileInput):
    """
    A widget to be used by the MultiFileField to allow the user to upload
    multiple files at one time.
    """

    def __init__(self, attrs=None):
        """
        Create a MultiFileInput.
        The 'count' attribute can be specified to default the number of
        file boxes initially presented.
        """
        super(MultiFileInput, self).__init__(attrs)
        self.attrs = {'count':1}
        if attrs:
            self.attrs.update(attrs)

    def render(self, name, value, attrs=None):
        """
        Renders the MultiFileInput.
        Should not be overridden.  Instead, subclasses should override the
        js, link, and/or fields methods which provide content to this method.
        """
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name+'[]')
        count = final_attrs['count']
        if count<1: count=1
        del final_attrs['count']

        js = self.js(name, value, count, final_attrs)
        link = self.link(name, value, count, final_attrs)
        fields = self.fields(name, value, count, final_attrs)

        return js+fields+link


    def add_file(self, doc, url, size, doc_id):
        #import ipdb; ipdb.set_trace()
        return u"""
                    <a href="%(url)s">%(doc)s</a>%(size)s
                    <input type="checkbox" name="del_doc" id=%(doc_id)s value="%(doc_id)s" />
                    <label for="%(doc_id)s"> Supprimer <i class="icon-trash"></i></label>
                    <br>
                """ % { 'doc': doc, 'url': url, 'size': size, 'doc_id': doc_id }




    def fields(self, name, value, count, attrs=None):
        """
        Renders the necessary number of file input boxes.
        """
        html =''
        if value:
            for doc in value:
                if not isinstance(doc, InMemoryUploadedFile):
                    html += self.add_file(doc.filename(), doc.doc.url, defaultfilters.filesizeformat(doc.doc.file.size), doc.id )

        html += u''.join([u'''<input%(inputstr)s style="display:none" onchange="$('#%(fakeinput)s').val($(this).val());"/>
                            <div class="input-append" id="%(divfakeinput)s">
                            <input id="%(fakeinput)s" class="input-small" type="text" readonly="readonly"/>
                            <a class="btn" onclick="$('input[id=%(id)s]').click();">Browse</a>
                            </div>
                            <br/>\n''' % { 'inputstr':flatatt(dict(attrs, id=attrs['id']+str(i))),
                                          'id':attrs['id']+str(i), 'fakeinput':'fakeinput'+str(i), 'divfakeinput':'divfakeinput'+str(i)}
                         for i in range(count)])
        return html

    def link(self, name, value, count, attrs=None):
        """
        Renders a link to add more file input boxes.
        """
        return u'<a onclick="javascript:new_%(name)s()" id="add_file">Ajouter un autre fichier</a>' % {'name':name}

    def js(self, name, value, count, attrs=None):
        """
        Renders a bit of Javascript to add more file input boxes.
        OUILLE OUILE OUILLE
        TODO refaire en jquery !!
        """
        return u"""
        <script type="text/javascript">
        <!--
        %(id)s_counter=%(count)d;
        function new_%(name)s() {
            b=document.getElementById('%(id)s0');
            e=document.getElementById('divfakeinput0');
            c=b.cloneNode(false);
            c.id='%(id)s'+(%(id)s_counter);
            c.value=""
            c.attributes['onchange'].nodeValue="$('#fakeinput" + %(id)s_counter + "').val($(this).val());";
            f=e.cloneNode(true);
            f.id='divfakeinput'+(%(id)s_counter);
            f.children[0].id="fakeinput"+%(id)s_counter;
            f.children[0].value="";
            f.children[1].attributes['onclick'].nodeValue="$('input[id=%(id)s" +  %(id)s_counter + "]').click();";
            b.parentNode.insertBefore(c,document.getElementById("add_file"));
            b.parentNode.insertBefore(f,document.getElementById("add_file"));
            b.parentNode.insertBefore(document.createElement("br"),document.getElementById("add_file"));
            %(id)s_counter++;
        };
       -->
        </script>
        """ % {'id':attrs['id'], 'name':name, 'count':count}

    def value_from_datadict(self, data, files, name):
        """
        File widgets take data from FILES, not POST.
        """
        name = name+'[]'
        if isinstance(files, MultiValueDict):
            return files.getlist(name)
        else:
            return None

    def id_for_label(self, id_):
        """
        The first file input box always has a 0 appended to it's id.
        """
        if id_:
            id_ += '0'
        return id_
    id_for_label = classmethod(id_for_label)

class MultiFileField(Field):
    """
    A field allowing users to upload multiple files at once.
    """
    widget = MultiFileInput
    count = 1

    def __init__(self, count=1, strict=False, *args, **kwargs):
        """
        strict is whether the number of files uploaded must equal count
        """
        self.count = count
        self.strict = strict
        super(MultiFileField, self).__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        """
        Adds the count to the MultiFileInput widget.
        """
        if isinstance(widget, MultiFileInput):
            return {'count':self.count}
        return {}

    def clean(self, data):
        """
        Cleans the data and makes sure that all the files had some content.
        Also checks whether a file was required.
        """
        super(MultiFileField, self).clean(data)

        if not self.required and data in EMPTY_VALUES:
            return None
        try:
            f = map(lambda a: UploadedFile(file=a.file, name=a.name, content_type=a.content_type, size=a.size, charset=a.charset), data)
        except TypeError:
            raise ValidationError(ugettext(u"No file was submitted. Check the encoding type on the form."))
        except KeyError:
            raise ValidationError(ugettext(u"No file was submitted."))

        for a_file in f:
            if not a_file.content_type:
                raise ValidationError(ugettext(u"The submitted file is empty."))

        if self.strict and len(f) != self.count:
            raise ValidationError(ugettext(u"An incorrect number of files were uploaded."))

        return f

class FixedMultiFileInput(MultiFileInput):
    """
    A MultiFileInput widget that doesn't print the javascript code to allow
    the user to add more file input boxes.
    """
    def link(self, name, value, count, attrs=None):
        return u''

    def js(self, name, value, count, attrs=None):
        return u''
