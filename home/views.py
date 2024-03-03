from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, logout, login
from .forms import (
    SigninForm,
    SignupForm,
    SignupCodeForm,
    SignupCompletedForm,
    ForgotPassForm,
    ForgotPassCodeForm,
    ForgotPassCompletedForm,
    ContactUsForm
)
from blog import models as blog_models
from shop import models as shop_models
import uuid
from django.contrib.auth import get_user_model
from django.http import Http404
from django.conf import settings
import ghasedakpack, pyotp, hashlib
from . import models

User = get_user_model()
sms = ghasedakpack.Ghasedak(settings.SECRET_SMS)
totp = pyotp.TOTP(pyotp.random_base32())
from django.views import View
from django.shortcuts import render
from shop.models import CategoryProd,ProductProd,ProductImagesProd  # وارد کردن مدل CategoryProd از ماژول shop.models

class IndexView(View):
    def get(self, request):
        category_id = request.GET.get('category_id')
        if category_id:
            categories = CategoryProd.objects.filter(id=category_id)  # استفاده از مدل CategoryProd
        else:
            categories = CategoryProd.objects.all().order_by("-date_created")





        procat = ProductProd.objects.filter(category_id=category_id)
       
        posts = blog_models.Post.objects.all().order_by("-date_created")[:10]
        sliders = models.SliderContent.objects.all().order_by("-date_created")[:5]
        context = {"categories": categories, "posts": posts, "sliders": sliders,"procat":procat}
        return render(request, "home/index.html", context)


class LoginView(View):
    def get(self, request):
        form = SigninForm()
        context = {"form": form}
        return render(request, "home/login.html", context)

    def post(self, request):
        form = SigninForm(request.POST)
        redirect_to = (
            request.GET.get("redirect_to") if request.GET.get("redirect_to") else "/"
        )

        context = {"form": form}
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(f"{redirect_to}")
            else:
                return render(request, "home/login.html", context)
        else:
            return render(request, "home/login.html", context)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home:home")


class SignupView(View):
    def get(self, request):
        form = SignupForm()
        context = {"form": form}
        return render(request, "home/signup.html", context)

    def post(self, request):
        form = SignupForm(request.POST)
        context = {"form": form}
        if form.is_valid():
            phone = form.cleaned_data["username"]
            user = None
            try:
                user = User.objects.filter(phone__exact=phone).first()
                if user is None:
                    token = totp.now()
                    refid = str(uuid.uuid4())
                    request.session["signup_refid"] = refid
                    request.session["signup_phone"] = phone
                    request.session["signup_token"] = hashlib.sha256(
                        str(token).encode()
                    ).hexdigest()

                    is_sms_sent=sms.verification(
                        {
                            "receptor": phone,
                            "type": "1",
                            "template": "bornaverify",
                            "param1": token,
                        }
                    )
                    print(f"Verification code is sent to {phone} successfuly! and status: {is_sms_sent}")
                    return redirect("home:signup-code", refid=refid)
                else:
                    return redirect("home:signup")
            except Exception as e:
                print(e)
                return render(request, "home/signup.html", context)
        else:
            return render(request, "home/signup.html", context)


class SignupCodeView(View):
    def get(self, request, refid):
        if refid == request.session.get("signup_refid"):
            form = SignupCodeForm()
            context = {"phone": request.session.get("signup_phone"), "form": form}
            return render(request, "home/signup-code.html", context)
        else:
            raise Http404("Page not found!")

    def post(self, request, refid=None):
        refid1 = request.session.get("signup_refid")
        form = SignupCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            if hashlib.sha256(str(code).encode()).hexdigest() == request.session.get(
                "signup_token"
            ):
                refid2 = str(uuid.uuid4())
                request.session["signup_refid"] = refid2
                request.session["signup_flag"] = hashlib.sha256(
                    str("True" + "bornaabzar").encode()
                ).hexdigest()
                return redirect("home:signup-completed", refid=refid2)

            else:
                request.session["signup_flag"] = hashlib.sha256(
                    str("False" + "bornaabzar").encode()
                ).hexdigest()
                return redirect("home:signup-code", refid=refid1)
        else:
            return redirect("home:signup-code", refid=refid1)


class SignupCompletedView(View):
    def get(self, request, refid):
        if refid == request.session.get("signup_refid"):
            form = SignupCompletedForm()
            context = {"form": form}
            return render(request, "home/signup-completed.html", context)
        else:
            raise Http404("Page not found!")

    def post(self, request, refid=None):
        refid1 = request.session.get("signup_refid")
        form = SignupCompletedForm(request.POST)
        if form.is_valid():
            fullname = form.cleaned_data["fullname"]
            email = form.cleaned_data["email"]
            password1 = form.cleaned_data["password"]
            password2 = form.cleaned_data["re_password"]
            if (
                request.session.get("signup_flag")
                == hashlib.sha256(str("True" + "bornaabzar").encode()).hexdigest()
            ):
                user = User(
                    phone=request.session.get("signup_phone"),
                    fullname=fullname,
                    email=email,
                )
                user.set_password(password1)
                user.save()
                login(request, user)
                return redirect("dashboard:profile")

            else:
                return redirect("home:signup-completed", refid=refid1)
        else:
            return redirect("home:signup-completed", refid=refid1)


class ForgotPassView(View):
    def get(self, request):
        form = ForgotPassForm()
        context = {"form": form}
        return render(request, "home/forgot-pass.html", context)

    def post(self, request):
        form = ForgotPassForm(request.POST)
        context = {"form": form}
        if form.is_valid():
            phone = form.cleaned_data["username"]
            user = None
            try:
                user = User.objects.get(phone__exact=phone)
                if user is not None:
                    token = totp.now()
                    refid = str(uuid.uuid4())
                    request.session["forgot_pass_refid"] = refid
                    request.session["forgot_pass_phone"] = phone
                    request.session["forgot_pass_token"] = hashlib.sha256(
                        str(token).encode()
                    ).hexdigest()

                    sms.verification(
                        {
                            "receptor": phone,
                            "type": "1",
                            "template": "bornaverify",
                            "param1": token,
                        }
                    )
                    print(f"Verification code is sent to {phone} successfuly!")
                    return redirect("home:forgot-pass-code", refid=refid)
            except Exception as e:
                print(e)
                return render(request, "home/forgot-pass.html", context)
        else:
            return render(request, "home/forgot-pass.html", context)


class ForgotPassCodeView(View):
    def get(self, request, refid):
        if refid == request.session.get("forgot_pass_refid"):
            form = ForgotPassCodeForm()
            context = {"phone": request.session.get("forgot_pass_phone"), "form": form}
            return render(request, "home/forgot-pass-code.html", context)
        else:
            raise Http404("Page not found!")

    def post(self, request, refid=None):
        refid1 = request.session.get("forgot_pass_refid")
        form = ForgotPassCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            if hashlib.sha256(str(code).encode()).hexdigest() == request.session.get(
                "forgot_pass_token"
            ):
                refid2 = str(uuid.uuid4())
                request.session["forgot_pass_refid"] = refid2
                request.session["forgot_pass_flag"] = hashlib.sha256(
                    str("True" + "bornaabzar").encode()
                ).hexdigest()
                return redirect("home:forgot-pass-completed", refid=refid2)

            else:
                request.session["forgot_pass_flag"] = hashlib.sha256(
                    str("False" + "bornaabzar").encode()
                ).hexdigest()
                return redirect("home:forgot-pass-code", refid=refid1)
        else:
            return redirect("home:forgot-pass-code", refid=refid1)


class ForgotPassCompletedView(View):
    def get(self, request, refid):
        if refid == request.session.get("forgot_pass_refid"):
            form = ForgotPassCompletedForm()
            context = {"form": form}
            return render(request, "home/forgot-pass-completed.html", context)
        else:
            raise Http404("Page not found!")

    def post(self, request, refid=None):
        refid1 = request.session.get("forgot_pass_refid")
        form = ForgotPassCompletedForm(request.POST)
        context = {"form": form}
        if form.is_valid():
            password1 = form.cleaned_data["password"]
            password2 = form.cleaned_data["re_password"]
            if (
                request.session.get("forgot_pass_flag")
                == hashlib.sha256(str("True" + "bornaabzar").encode()).hexdigest()
            ):
                user = User.objects.get(
                    phone__exact=request.session.get("forgot_pass_phone")
                )
                user.set_password(password1)
                user.save()
                return redirect("home:login")

            else:
                return redirect("home:forgot-pass-completed", refid=refid1)
        else:
            return redirect("home:forgot-pass-completed", refid=refid1)


class AboutUsView(View):
    def get(self, request):
        context = {}
        return render(request, "home/about-us.html", context)


class ContactUsView(View):
    def get(self, request):
        form = ContactUsForm()
        context = {"form":form}
        return render(request, "home/contact-us.html", context)
    
    def post(self, request):
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home:contact")
        else:
            return render(request, "home:contact", {"form": form})


class SurveyView(View):
    def get(self, request):
        context = {}
        return render(request, "home/survey.html", context)
