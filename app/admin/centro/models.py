#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db

class Centro(db.Document):
	#__tablename__ = 'centro'

	citta = db.StringField(max_length=50)
	provincia = db.StringField(max_length=2,min_length=2)
	indirizzo = db.StringField(max_length=100)

	def __unicode__(self):
		return '%s - %s' % (self.citta, self.indirizzo)
