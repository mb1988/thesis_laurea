# -*- coding: utf-8 -*-
from app.admin.paziente.models import Paziente
from app.admin.forms import MyModelView

from flask import render_template

from flask_weasyprint import HTML, render_pdf

from app import app

class PazienteAdmin(MyModelView):

	list_template = 'admin/model/list_pazienti.html'

	column_list = ('cognome','nome','nascita','medico','centro')
	
	column_searchable_list = ('cognome','nome')
	
	column_filters = ('cognome',
                      'nome',
                      'nascita')
                      
	@app.route('/pazienti.pdf')
	def pazienti_pdf():
		pazienti = Paziente.objects.all()
		html = render_template('pazienti_list.html',pazienti=pazienti)
		return render_pdf(HTML(string=html))
                        
