# -*- coding: utf-8 -*-
from app.admin.forms import MyModelView
from app.admin.medico.models import Medico
from app.admin.centro.models import Centro

from flask import render_template

from flask_weasyprint import HTML, render_pdf

from app import app

class MedicoAdmin(MyModelView):

	list_template = 'admin/model/list_medici.html'

	column_list = ('cognome','nome','centro')

	column_searchable_list = ('cognome','nome')

	column_filters = ('cognome',
                      'nome')
                     
	@app.route('/medici.pdf')
	def medici_pdf():
		medici = Medico.objects.all()
		html = render_template('medici_list.html',medici=medici)
		return render_pdf(HTML(string=html))
   
