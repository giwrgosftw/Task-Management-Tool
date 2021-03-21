from models import project
from wtforms_alchemy import ModelForm
from wtforms import Form, StringField, validators
from wtforms.validators import DataRequired, Regexp

class myForm(Form):
    """Homepage form."""
    PlotlyURL = StringField('https://github.com/google/deepdream/blob/master/dream.ipynb',
    validators=[
            DataRequired(),
            Regexp(".*\.ipynb$",
            message="Please provide a URL ending in ipynb"),
          ])

class ProjectForm(ModelForm):
    class Meta:
        model = project.Project
