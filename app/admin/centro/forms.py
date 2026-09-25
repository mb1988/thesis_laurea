# -*- coding: utf-8 -*-
from app.admin.forms import MyModelView
from app.admin.centro.models import Centro

from flask import render_template

from flask_weasyprint import HTML, render_pdf

from app import app


class CentroAdmin(MyModelView):

    list_template = 'admin/model/list_centri.html'

    menu_icon_type = 'fa'
    menu_icon_value = 'fa-hospital-o'

    column_labels = dict(citta=u'Città', provincia=u'Provincia', indirizzo=u'Indirizzo')

    column_searchable_list = ('citta','provincia','indirizzo')

    column_filters = ('citta',
                      'provincia',
                      'indirizzo')

    column_default_sort = 'citta'

    form_args = dict(
        provincia=dict(description=u'Sigla della provincia (due lettere), es. MI.'),
    )

    @app.route('/centri.pdf')
    def centri_pdf():
        centri = Centro.objects.all()
        html = render_template('centri_list.html',centri=centri)
        return render_pdf(HTML(string=html))
