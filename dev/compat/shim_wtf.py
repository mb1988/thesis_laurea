# -*- coding: utf-8 -*-
"""``flask.ext.wtf`` shim.

Flask-WTF 0.x re-exported WTForms 1.x, where the text field was called
``TextField`` and validators were lowercase classes you instantiate
(``validators=[required()]``).  Flask-WTF 1.x renamed those.  This module keeps
the old names working so the project forms do not have to change.
"""

from flask_wtf import FlaskForm  # noqa: F401
from wtforms import (BooleanField, DateField, DateTimeField,  # noqa: F401
                     DecimalField, Field, FileField, FloatField, HiddenField,
                     IntegerField, PasswordField, SelectField,
                     SelectMultipleField, StringField, SubmitField,
                     TextAreaField, validators)
from wtforms.validators import ValidationError  # noqa: F401

# WTForms 1.x names kept for the legacy call sites.
Form = FlaskForm
TextField = StringField
required = validators.DataRequired

__all__ = [
    "Form", "FlaskForm", "TextField", "StringField", "PasswordField",
    "BooleanField", "IntegerField", "DateField", "DateTimeField",
    "DecimalField", "FloatField", "FileField", "HiddenField", "SelectField",
    "SelectMultipleField", "TextAreaField", "SubmitField", "Field",
    "validators", "ValidationError", "required",
]
