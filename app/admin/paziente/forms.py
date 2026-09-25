# -*- coding: utf-8 -*-
from app.admin.paziente.models import Paziente
from app.admin.forms import MyModelView

from flask import render_template

from flask_weasyprint import HTML, render_pdf

from app import app


class PazienteAdmin(MyModelView):

    list_template = 'admin/model/list_pazienti.html'

    menu_icon_type = 'fa'
    menu_icon_value = 'fa-users'

    column_list = ('cognome','nome','nascita','medico','centro')

    column_labels = dict(cognome=u'Cognome', nome=u'Nome', nascita=u'Data di nascita',
                         medico=u'Medico', centro=u'Centro')

    column_searchable_list = ('cognome','nome')

    column_filters = ('cognome',
                      'nome',
                      'nascita')

    column_default_sort = [('cognome', False), ('nome', False)]

    @app.route('/pazienti.pdf')
    def pazienti_pdf():
        pazienti = Paziente.objects.all()
        html = render_template('pazienti_list.html',pazienti=pazienti)
        return render_pdf(HTML(string=html))
