from django import forms
from django.forms import ModelForm
from django.forms.widgets import TextInput
from .models import Tag, DataSet


class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"
        widgets = {
            "colour": TextInput(attrs={'type': 'color'}),
        }


class DatasetForm(ModelForm):

    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=True)

    class Meta:
        model = DataSet
        fields = "__all__"
