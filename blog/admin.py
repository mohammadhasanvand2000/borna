from django.contrib import admin
from . import models

@admin.register(models.Category)
class BlgCategory(admin.ModelAdmin):
    list_display= ["title", "get_user", "get_parent"]

    def get_user(self, obj):
        return obj.user.fullname or "-"
    
    def get_parent(self, obj):
        return obj.parent.title if obj.parent else "-"

@admin.register(models.Post)
class BlgPost(admin.ModelAdmin):
    list_display= ["title", "get_user", "get_cat"]

    def get_user(self, obj):
        return obj.user.fullname or "-"
    
    def get_cat(self, obj):
        return obj.category.title or "-"

@admin.register(models.PostImages)
class BlogPostImage(admin.ModelAdmin):
    list_display= ["get_user", "get_post"]

    def get_user(self, obj):
        return obj.user.fullname or "-"
    
    def get_post(self, obj):
        return obj.post.title or "-"


@admin.register(models.Comment)
class BlogComment(admin.ModelAdmin):
    list_display= ["comment", "get_user", "get_post", "get_parent"]

    def get_user(self, obj):
        return obj.user.fullname if obj.user else "-"
    
    def get_post(self, obj):
        return obj.post.title or "-"
    
    def get_parent(self, obj):
        return obj.parent.user.fullname if obj.parent and obj.parent.user else "-"
