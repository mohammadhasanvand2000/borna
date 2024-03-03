from django.contrib import admin
from . import models

@admin.register(models.SliderContent)
class SliderContentAdmin(admin.ModelAdmin):
    list_display=["small_title", "big_title"]
