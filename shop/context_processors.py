from . import models


def shop_cat(request):
    return {
        "shop_cat": models.CategoryProd.objects.all()
        
    }
