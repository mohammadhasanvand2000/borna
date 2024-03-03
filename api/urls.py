from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
  path('cart/<int:flag>/<int:id>/',views.UpdateCartAPI.as_view(), name='cart'),
]