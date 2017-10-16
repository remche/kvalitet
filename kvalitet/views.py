# -*- coding: utf-8 -*-
from fchach.views import FchAchListView

class TableauBordView(FchAchListView):
    template_name = "tableaubord.html"

    def get_context_data(self, **kwargs):
        context = super(TableauBordView, self).get_context_data(**kwargs)
        context['view_type_menu'] = ''
        return context
