from django.contrib import admin
from . import models

@admin.register(models.Category)
class CaregoryAdmin(admin.ModelAdmin):
    list_display=["title", "description", "get_parent"]

    def get_parent(self, obj):
        return obj.parent.title if obj.parent else "-"

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=["title", "description", "disabled", "get_cat"]

    def get_cat(self, obj):
        return obj.category.title


@admin.register(models.ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display=["get_product"]

    def get_product(self, obj):
        return obj.product.title

@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display=["review", "rate", "get_user", "get_product"]

    def get_user(self, obj):
        return obj.user.fullname or "-"
    
    def get_product(self, obj):
        return obj.product.title

@admin.register(models.CategoryProd)
class ProdCaregoryAdmin(admin.ModelAdmin):
    list_display=["title", "description"]

@admin.register(models.ProductProd)
class ProdProductAdmin(admin.ModelAdmin):
    list_display=["title", "description", "disabled", "get_cat"]

    def get_cat(self, obj):
        return obj.category.title


@admin.register(models.ProductImagesProd)
class ProdProductImagesAdmin(admin.ModelAdmin):
    list_display=["get_product"]

    def get_product(self, obj):
        return obj.product.title

@admin.register(models.ReviewProd)
class ProdReviewAdmin(admin.ModelAdmin):
    list_display=["review", "rate", "get_user", "get_product"]

    def get_user(self, obj):
        return obj.user.fullname or "-"
    
    def get_product(self, obj):
        return obj.product.title

@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display=["invoice_number", "name", "phone", "count", "sub_total", "shipping", "total"]

@admin.register(models.Payment)
class InvoiceAdmin(admin.ModelAdmin):
    list_display=["date_created", "date_modified", "user", "status"]

