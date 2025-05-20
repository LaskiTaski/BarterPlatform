from django.urls import path
from . import views
from .views import signup

urlpatterns = [
    path('', views.ad_list, name='ad_list'),
    path('ad/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('ad/create/', views.ad_create, name='ad_create'),
    path('ad/<int:pk>/edit/', views.ad_update, name='ad_update'),
    path('ad/<int:pk>/delete/', views.ad_delete, name='ad_delete'),
    path('ad/<int:ad_receiver_pk>/exchange/', views.exchangeproposal_create, name='exchangeproposal_create'),

    path("accounts/signup/", signup, name="signup"),

    path('accounts/messages/', views.my_exchange_proposals, name='my_exchange_proposals'),

    path('exchange/<int:pk>/accept/', views.exchangeproposal_accept, name='exchangeproposal_accept'),
    path('exchange/<int:pk>/decline/', views.exchangeproposal_decline, name='exchangeproposal_decline'),

]
