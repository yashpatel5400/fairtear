"""
__author__ = Yash Patel and Zachary Liu
__name__   = app.py
__description__ = Flask Form objects definitions
"""

from flask_wtf import Form, FlaskForm

from flask_wtf.file import FileField, FileRequired
from wtforms.validators import InputRequired
from wtforms import StringField, SelectField, FloatField, FileField, FormField

def ConditionalField(label, required=True):
    validators = [InputRequired()] if required else []
    return SelectField(label, choices=[(">", ">"), ("=", "="), ("<", "<")], validators=validators)

def AttributeFormClass(required=True):
    validators = [InputRequired()] if required else []
    class AttributeForm(Form):
        attribute   = StringField("Attribute", validators=validators)
        conditional = SelectField("Conditional", choices=[(">", ">"), ("=", "="), ("<", "<")], validators=validators)
        threshold   = FloatField("Threshold", validators=validators)
    return AttributeForm

class DataForm(FlaskForm):
    xcsv  = FileField("Features CSV")
    ycsv  = FileField("Target CSV")
    clf   = FileField("Classifier Pickle")

    sensitive = FormField(AttributeFormClass())
    qualified = FormField(AttributeFormClass(required=False))
    target = FormField(AttributeFormClass())
