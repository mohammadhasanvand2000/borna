from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from . import models


class MyAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("phone", "password", "salt")}),
        (_("Personal info"), {"fields": ("fullname", "first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "phone",
                    "password1",
                    "password2",
                    "salt",
                    "fullname",
                    "first_name",
                    "last_name",
                    "email",
                )
            },
        ),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "is_superuser", "date_joined")},
        ),
    )
    list_display = (
        "phone",
        "email",
        "fullname",
        "salt",
        "is_active",
        "is_staff",
        "is_superuser",
    )


admin.site.register(models.User, MyAdmin)

