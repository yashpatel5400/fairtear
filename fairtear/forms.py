"""
__author__ = Yash Patel and Zachary Liu
__name__   = app.py
__description__ = Flask Form objects definitions
"""

from flask_wtf import Form, FlaskForm

from flask_wtf.file import FileField, FileRequired
from wtforms.validators import InputRequired
from wtforms import StringField, SelectField, FloatField, FileField, FormField, BooleanField

def ConditionalField(label, required=True):
    validators = [InputRequired()] if required else []
    return SelectField(label, choices=[(">", ">"), ("=", "="), ("<", "<")], validators=validators)

class AttributeForm(Form):
    attribute   = StringField("Attribute", validators=[InputRequired()])
    conditional = SelectField("Conditional", choices=[(">", ">"), ("=", "="), ("<", "<")], validators=[InputRequired()])
    threshold   = FloatField("Threshold", validators=[InputRequired()])

class DataForm(FlaskForm):
    xcsv  = FileField("Data CSV", validators=[InputRequired()])
    clf   = FileField("Classifier Pickle", validators=[InputRequired()])

    sensitive = FormField(AttributeForm)
    enable_qualified = BooleanField()
    qualified = FormField(AttributeForm)
    target = FormField(AttributeForm)
