from django import forms


class ReviewForm(forms.Form):
    name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    rate = forms.FloatField(required=False, max_value=5, min_value=0, step_size=0.5)
    review = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows": 4}))


class DiscountForm(forms.Form):
    discount = forms.CharField(required=True)


class CustomerForm(forms.Form):
    name = forms.CharField(required=True, max_length=128)
    company = forms.CharField(required=False, max_length=128)
    address = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows": 2}))
    zipcode = forms.CharField(required=True, max_length=15)
    phone = forms.CharField(required=True, max_length=15)
    email = forms.EmailField(required=False)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 4}))