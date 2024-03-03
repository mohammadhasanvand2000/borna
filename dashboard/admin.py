from django.contrib import admin
from . import models


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display =('get_fullname', 'get_phone', 'get_active', 'get_superuser')
    def get_fullname(self, obj):
        return obj.user.fullname
    def get_phone(self, obj):
        return obj.user.phone
    def get_active(self, obj):
        return obj.user.is_active
    def get_superuser(self, obj):
        return obj.user.is_superuser