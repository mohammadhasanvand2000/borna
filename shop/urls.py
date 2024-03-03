from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.ShopListView.as_view(), name='shop-list'),
    path('cat=<cat_id>/', views.ShopListCatView.as_view(), name='cat-list'),
    path('product=<product_id>/', views.ShopDetailView.as_view(), name='shop-detail'),
    path('tag=<tag_slug>/',views.ShopListTagView.as_view(), name='shop-tag'),
    
    path('main-products', views.ProdShopListView.as_view(), name='prod-shop-list'),
    path('main-cat=<cat_id>/', views.ProdShopListCatView.as_view(), name='prod-cat-list'),
    path('main-product=<product_id>/', views.ProdShopDetailView.as_view(), name='prod-shop-detail'),
    path('main-tag=<tag_slug>/',views.ProdShopListTagView.as_view(), name='prod-tag'),
    
    path('cart/', views.ShopCartView.as_view(), name='cart'),
    path('checkout/', views.ShopCheckoutView.as_view(), name='checkout'),
    path('order-completed/', views.ShopCompleteView.as_view(), name='complete'),
]