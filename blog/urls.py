from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog-list'),
    path('post=<blog_id>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('cat=<blog_id>/', views.BlogCatListView.as_view(), name='blog-cat'),
    path('tag=<tag_slug>/',views.TagListView.as_view(), name='blog-tag')
]