
from django import forms
from django.forms import ModelForm
from .models import Member


class MemberForm(ModelForm):

    password = forms.CharField(required=False)

    class Meta:
        model = Member
        fields = [
            'username', 'email', 'password',
            'is_datascientist', 'is_annotator', 'first_name', 'last_name',
            'is_active', 'first_name', 'last_name',
        ]
        widgets = {
            'password': forms.PasswordInput()
        }
