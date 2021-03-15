from models import project
from wtforms_alchemy import ModelForm


class ProjectForm(ModelForm):
    class Meta:
        model = project.Project
