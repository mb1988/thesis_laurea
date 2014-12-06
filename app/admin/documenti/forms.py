# -*- coding: utf-8 -*-
from app.admin.forms import MyModelView
from app.admin.documenti.models import Questionario_ingresso, Modulo_CDP, Questionario_followup

#from flaskext.mongoengine.wtf import model_form
from flask.ext.mongoengine.wtf.fields import QuerySetSelectField

from flask import render_template, request, url_for, redirect, flash
from flask.ext.admin.form import Select2Field, Select2Widget, DatePickerWidget
from flask.ext.admin.base import expose
from flask.ext.admin.babel import gettext
from flask.ext import wtf
from flask.ext.wtf import Form, TextField, BooleanField, StringField,IntegerField, DateField, TextAreaField
from app.admin.paziente.models import Paziente

import json

from flask_weasyprint import HTML, render_pdf
from app import app, db

quest_ingresso_data=open('questionario_ingresso.json')
quest_ingresso = json.load(quest_ingresso_data)
quest_ingresso_data.close()

quest_followup_data=open('questionario_followup.json')
quest_followup = json.load(quest_followup_data)
quest_followup_data.close()

mod_data=open('modulo.json')
mod = json.load(mod_data)
mod_data.close()

class QuestionarioIngressoForm(Form):
	pass
	
class QuestionarioFollowupForm(Form):
	pass

class ModuloForm(Form):
	pass

def generate_field(dom):
	if dom["type"]=="StringField":
		return StringField(dom["label"])
	if dom["type"]=="IntegerField":#metto string perche integer è required
		return StringField(dom["label"])
	if dom["type"]=="BooleanField":
		return BooleanField(dom["label"])
	if dom["type"]=="TextField":
		return TextField(dom["label"])
	if dom["type"]=="TextAreaField":
		return TextAreaField(dom["label"])
	if dom["type"]=="DateField":#string
		return StringField(dom["label"])
	if dom["type"]=="TimeField":#string
		return StringField(dom["label"])
	if dom["type"]=="SelectField":
		choices = dom["choices"].items()
		return Select2Field(dom["label"],choices = choices)

class QuestionarioIngressoAdmin(MyModelView):

	list_template = 'admin/model/list_pdf.html'
	create_template = 'admin/model/create_questingr.html'
	edit_template = 'admin/model/edit_questingr.html'
	
	@expose('/new/', methods=('GET', 'POST'))
	def create_view(self):
		return_url = request.args.get('url') or url_for('.index_view')
		
		if not self.can_create:
			return redirect(return_url)
		
		paziente=Paziente.objects.all()
		setattr(QuestionarioIngressoForm,'paziente',QuerySetSelectField(queryset=paziente,label = u'Paziente',widget=Select2Widget()))
		
		for dom in quest_ingresso:
			field = generate_field(dom)
			setattr(QuestionarioIngressoForm,dom["name"],field)
		
		form = QuestionarioIngressoForm(request.form)

		
		
		if form.validate_on_submit():
			questionario_ingresso = Questionario_ingresso()
			form.populate_obj(questionario_ingresso)
			questionario_ingresso.save()
			#if self.create_model(form):
			if '_add_another' in request.form:
				flash(gettext('Model was successfully created.'))
				return redirect(url_for('.create_view', url=return_url))
			else:
				return redirect(return_url)
				
		return self.render(self.create_template,
                           form=form,
                           return_url=return_url)
                           
	@expose('/edit/', methods=('GET', 'POST'))
	def edit_view(self):
		return_url = request.args.get('url') or url_for('.index_view')
		if not self.can_edit:
			return redirect(return_url)
			
		id = request.args.get('id')
		if id is None:
			return redirect(return_url)
			
		model = self.get_one(id)
		
		if model is None:
			return redirect(return_url)
		
		
		paziente=Paziente.objects.all()
		setattr(QuestionarioIngressoForm,'paziente',QuerySetSelectField(queryset=paziente,label = u'Paziente',widget=Select2Widget()))
		for dom in quest_ingresso:
			field = generate_field(dom)
			setattr(QuestionarioIngressoForm,dom["name"],field)
		
		form = QuestionarioIngressoForm(request.form, obj=model)	
		#form = self.edit_form(obj=model)
		
		if form.validate_on_submit():
			if self.update_model(form, model):
				return redirect(return_url)
				
		return self.render(self.edit_template,
                               form=form,
                               return_url=return_url)
                               
	@expose('/questionario_ingresso.pdf', methods=('GET', 'POST'))
	def pdf(self):
		id = request.args.get('id')
		document = Questionario_ingresso.objects.get(id=id)

		html = render_template('questionario_ingresso.html',model=quest_ingresso,document=document.__dict__,quest_ingresso=document)
		return render_pdf(HTML(string=html))
                          
class QuestionarioFollowupAdmin(MyModelView):

	list_template = 'admin/model/list_pdf.html'
	create_template = 'admin/model/create_questfoll.html'
	edit_template = 'admin/model/edit_questfoll.html'
	
	@expose('/new/', methods=('GET', 'POST'))
	def create_view(self):
		return_url = request.args.get('url') or url_for('.index_view')
		
		if not self.can_create:
			return redirect(return_url)
		
		paziente=Paziente.objects.all()
		setattr(QuestionarioFollowupForm,'paziente',QuerySetSelectField(queryset=paziente,label = u'Paziente',widget=Select2Widget()))
		
		for dom in quest_followup:
			field = generate_field(dom)
			setattr(QuestionarioFollowupForm,dom["name"],field)
		
		form = QuestionarioFollowupForm(request.form)

		
		
		if form.validate_on_submit():
			questionario_followup = Questionario_followup()
			form.populate_obj(questionario_followup)
			questionario_followup.save()
			#if self.create_model(form):
			if '_add_another' in request.form:
				flash(gettext('Model was successfully created.'))
				return redirect(url_for('.create_view', url=return_url))
			else:
				return redirect(return_url)
				
		return self.render(self.create_template,
                           form=form,
                           return_url=return_url)
                           
	@expose('/edit/', methods=('GET', 'POST'))
	def edit_view(self):
		return_url = request.args.get('url') or url_for('.index_view')
		if not self.can_edit:
			return redirect(return_url)
			
		id = request.args.get('id')
		if id is None:
			return redirect(return_url)
			
		model = self.get_one(id)
		
		if model is None:
			return redirect(return_url)
		
		
		paziente=Paziente.objects.all()
		setattr(QuestionarioFollowupForm,'paziente',QuerySetSelectField(queryset=paziente,label = u'Paziente',widget=Select2Widget()))
		for dom in quest_followup:
			field = generate_field(dom)
			setattr(QuestionarioFollowupForm,dom["name"],field)
		
		form = QuestionarioFollowupForm(request.form, obj=model)	
		#form = self.edit_form(obj=model)
		
		if form.validate_on_submit():
			if self.update_model(form, model):
				return redirect(return_url)
				
		return self.render(self.edit_template,
                               form=form,
                               return_url=return_url)
                               
	@expose('/questionario_followup.pdf', methods=('GET', 'POST'))
	def pdf(self):
		id = request.args.get('id')
		document = Questionario_followup.objects.get(id=id)

		html = render_template('questionario_ingresso.html',model=quest_followup,document=document.__dict__,quest_ingresso=document)
		return render_pdf(HTML(string=html))
                               
class ModuloAdmin(MyModelView):

	list_template = 'admin/model/list_pdf.html'
                      
	@expose('/new/', methods=('GET', 'POST'))
	def create_view(self):
		return_url = request.args.get('url') or url_for('.index_view')
		
		if not self.can_create:
			return redirect(return_url)

		paziente=Paziente.objects.all()
		setattr(ModuloForm,'paziente',QuerySetSelectField(queryset=paziente,label = u'Paziente',widget=Select2Widget()))
		
		for dom in mod:
			field = generate_field(dom)
			setattr(ModuloForm,dom["name"],field)
		
		form = ModuloForm(request.form)

		
		
		if form.validate_on_submit():
			modulo = Modulo_CDP()
			form.populate_obj(modulo)
			modulo.save()
			#if self.create_model(form):
			if '_add_another' in request.form:
				flash(gettext('Model was successfully created.'))
				return redirect(url_for('.create_view', url=return_url))
			else:
				return redirect(return_url)
				
		return self.render(self.create_template,
                           form=form,
                           return_url=return_url)
                           
	@expose('/edit/', methods=('GET', 'POST'))
	def edit_view(self):
		return_url = request.args.get('url') or url_for('.index_view')
		if not self.can_edit:
			return redirect(return_url)
			
		id = request.args.get('id')
		if id is None:
			return redirect(return_url)
			
		model = self.get_one(id)
		
		if model is None:
			return redirect(return_url)
		
		paziente=Paziente.objects.all()
		setattr(ModuloForm,'paziente',QuerySetSelectField(queryset=paziente,label = u'Paziente',widget=Select2Widget()))
		for dom in mod:
			field = generate_field(dom)
			setattr(ModuloForm,dom["name"],field)
		
		form = ModuloForm(request.form, obj=model)	
		#form = self.edit_form(obj=model)
		
		if form.validate_on_submit():
			if self.update_model(form, model):
				return redirect(return_url)
				
		return self.render(self.edit_template,
                               form=form,
                               return_url=return_url)
                                

	@expose('/modulo_CDP.pdf')
	def pdf(self):
		id = request.args.get('id')
		document = Modulo_CDP.objects.get(id=id)
		
		html = render_template('modulo.html',model=mod,document=document.__dict__,quest=document)
		return render_pdf(HTML(string=html))



