from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('user-dashboard', views.DashboardUserHomeView.as_view(), name='user-home'),
    path('new-comments/', views.DashboardCommentsView.as_view(), name='comments'),
    path('new-reviews/', views.DashboardReviewsView.as_view(), name='reviews'),
    path('new-main-reviews/', views.DashboardMainProdReviewsView.as_view(), name='prod-reviews'),
    path('new-messages/', views.DashboardMessagesView.as_view(), name='messages'),
    path('users/', views.DashboardUsersView.as_view(), name='users'),
    path('users-add/', views.DashboardUsersAddView.as_view(), name='users-add'),
    path('users-edit/<str:uid>/', views.DashboardUsersEditView.as_view(), name='users-edit'),
    
    path('shop-categories/', views.DashboardShopCatView.as_view(), name='shop-cat'),
    path('main-shop-categories/', views.DashboardProdShopCatView.as_view(), name='prod-shop-cat'),
    
    path('shop-add/', views.DashboardShopAddView.as_view(), name='shop-add'),
    path('main-shop-add/', views.DashboardProdShopAddView.as_view(), name='prod-shop-add'),
    
    path('shop-edit/', views.DashboardShopEditView.as_view(), name='shop-edit'),
    path('main-shop-edit/', views.DashboardProdShopEditView.as_view(), name='prod-shop-edit'),
    
    path('shop-edit/reviews/prodid=<prod_id>/', views.DashboardProdReviewsView.as_view(), name='shop-reviews'),
    path('shop-edit/images/prodid=<prod_id>/', views.DashboardProductImagesView.as_view(), name='shop-images'),
    path('main-shop-edit/reviews/prodid=<prod_id>/', views.DashboardProdProdReviewsView.as_view(), name='prod-shop-reviews'),
    path('main-shop-edit/images/prodid=<prod_id>/', views.DashboardProdProductImagesView.as_view(), name='prod-shop-images'),
    
    path('shop-delete/', views.DashboardShopDeleteView.as_view(), name='shop-delete'),
    path('main-shop-delete/', views.DashboardProdShopDeleteView.as_view(), name='prod-shop-delete'),
    path('blog-categories/', views.DashboardBlogCatView.as_view(), name='blog-cat'),
    path('blog-add/', views.DashboardBlogAddView.as_view(), name='blog-add'),
    path('blog-edit/', views.DashboardBlogEditView.as_view(), name='blog-edit'),
    path('blog-edit/comments/postid=<post_id>/', views.DashboardBlogCommentsView.as_view(), name='blog-comments'),
    path('blog-delete/', views.DashboardBlogDeleteView.as_view(), name='blog-delete'),
    path('profile/', views.DashboardUserProfileView.as_view(), name='profile'),
    path('survey-list/', views.DashboardSurveyListView.as_view(), name='survey-list'),
    path('survey-detail/survey=<survey_token>', views.DashboardSurveyDetailView.as_view(), name='survey-detail'),
    path('sms/', views.DashboardSMSView.as_view(), name='sms'),
    path('slider/', views.DashboardSliderContentView.as_view(), name='slider'),
    path('slider/', views.DashboardSliderContentView.as_view(), name='slider'),
    path('slider/add/', views.DashboardSliderAddView.as_view(), name='slider-add'),
    
    # ordinary user permissions
    path('user-comments/', views.DashboardUserCommentsView.as_view(), name='user-comments'),
    path('user-reviews/', views.DashboardUserReviewsView.as_view(), name='user-reviews'),
    
    # financial
    path('fin-orders/', views.DashboardOrdersView.as_view(), name='fin-orders'),
    path('user-fin-orders/', views.DashboardUserOrdersView.as_view(), name='user-fin-orders'),
    path('fin-order/<int:invoice_num>/', views.DashboardOrderDetailView.as_view(), name='fin-order'),
    path('fin-transactions/', views.DashboardTransactionsView.as_view(), name='fin-transactions'),
    path('user-fin-transactions/', views.DashboardUserTransactionsView.as_view(), name='user-fin-transactions'),
    path('fin-pay/<int:invoice_num>/', views.PaymentAgainView.as_view(), name='fin-pay'),
]