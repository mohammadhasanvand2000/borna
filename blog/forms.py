from django import forms
from . import models

class CommentForm(forms.Form):
    name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    comment = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows": 4}))