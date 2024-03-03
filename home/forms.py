from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from captcha.fields import CaptchaField
from . import models


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = models.ContatcUs
        fields = "__all__"
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
        }


#  Sign in forms ...
class SigninForm(forms.Form):
    username = forms.CharField(
        required=True,
        error_messages={"required": "این فیلد الزامی می‌باشد."},
        validators=[],
    )
    password = forms.CharField(
        required=True, error_messages={"required": "این فیلد الزامی می‌باشد."}
    )

# Sign up forms ...
class SignupForm(forms.Form):
    username = forms.CharField(
        required=True,
        error_messages={"required": "این فیلد الزامی می‌باشد."},
        validators=[],
    )
    captcha = CaptchaField()


class SignupCodeForm(forms.Form):
    code = forms.IntegerField(
        required=True,
        error_messages={"required": "این فیلد الزامی می‌باشد."},
        validators=[],
    )


class SignupCompletedForm(forms.Form):
    fullname = forms.CharField(max_length=50)
    email = forms.EmailField(required=False)
    password = forms.CharField(
        required=True,
        error_messages={"required": "این فیلد الزامی می‌باشد."},
        widget=forms.PasswordInput(),
    )
    re_password = forms.CharField(
        required=True,
        error_messages={"required": "این فیلد الزامی می‌باشد."},
        widget=forms.PasswordInput(),
    )

    def clean_password(self):
        data = self.cleaned_data.get("password")
        if len(data) < 5:
            raise ValidationError("password must be at least 5 characters.")
        return data.strip()

    def clean(self):
        if self.cleaned_data.get("password") != self.cleaned_data.get("re_password"):
            raise ValidationError("password and confirmed password must be the same")
        return super().clean()


# forgot password forms ...
class ForgotPassForm(forms.Form):
    username = forms.CharField(
        required=True,
        error_messages={"required": "این فیلد الزامی می‌باشد."},
        validators=[],
    )
    captcha = CaptchaField()


class ForgotPassCodeForm(forms.Form):
    code = forms.IntegerField(
        required=True,
        error_messages={"required": "این فیلد الزامی می‌باشد."},
        validators=[],
    )


class ForgotPassCompletedForm(forms.Form):
    password = forms.CharField(
        required=True,
        error_messages={"required": "این فیلد الزامی می‌باشد."},
        widget=forms.PasswordInput(),
    )
    re_password = forms.CharField(
        required=True,
        error_messages={"required": "این فیلد الزامی می‌باشد."},
        widget=forms.PasswordInput(),
    )

    def clean(self):
        pass1 = self.cleaned_data["password"]
        pass2 = self.cleaned_data["re_password"]
        if pass1 == pass2:
            return self.cleaned_data
        else:
            raise ValidationError("pass1 and pass2 must be the same!")
