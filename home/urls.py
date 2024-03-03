
from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path(
        "signup-code/<str:refid>/", views.SignupCodeView.as_view(), name="signup-code"
    ),
    path(
        "signup-completed/<str:refid>/",
        views.SignupCompletedView.as_view(),
        name="signup-completed",
    ),
    path("forgot-password/", views.ForgotPassView.as_view(), name="forgot-password"),
    path(
        "forgot-pass-code/<str:refid>/",
        views.ForgotPassCodeView.as_view(),
        name="forgot-pass-code",
    ),
    path(
        "forgot-pass-completed/<str:refid>/",
        views.ForgotPassCompletedView.as_view(),
        name="forgot-pass-completed",
    ),
    path("about-us/", views.AboutUsView.as_view(), name="about"),
    path("contact-us/", views.ContactUsView.as_view(), name="contact"),
    path("survey/", views.SurveyView.as_view(), name="survey"),
]
