from django.urls import path

from .views.auth import SignupView

from .views.ad import (AdCreateView, AdUpdateView, AdDeleteView)
from .views.ad import (AdListView, AdDetailView)

from .views.exchange import (ExchangeProposalCreateView, MyExchangeProposalsView)
from .views.exchange import (ExchangeProposalAcceptView, ExchangeProposalDeclineView)

app_name = "ads"

urlpatterns = [
    # Регистрация
    path('accounts/signup/', SignupView.as_view(), name='signup'),

    # "Личный кабинет" — входящие предложения обмена
    path('accounts/messages/', MyExchangeProposalsView.as_view(), name='my_exchange_proposals'),

    # Список всех объявлений (главная)
    path('', AdListView.as_view(), name='ad_list'),
    # Просмотр одного объявления
    path('ad/<int:pk>/', AdDetailView.as_view(), name='ad_detail'),

    # Создать объявление
    path('ad/create/', AdCreateView.as_view(), name='ad_create'),
    # Редактировать объявление
    path('ad/<int:pk>/edit/', AdUpdateView.as_view(), name='ad_update'),
    # Удалить объявление
    path('ad/<int:pk>/delete/', AdDeleteView.as_view(), name='ad_delete'),

    # Создать предложение обмена (по чужому объявлению)
    path('ad/<int:ad_receiver_pk>/exchange/',
         ExchangeProposalCreateView.as_view(), name='exchangeproposal_create'),
    # Принять предложение обмена (POST)
    path('exchange/<int:pk>/accept/',
         ExchangeProposalAcceptView.as_view(), name='exchangeproposal_accept'),
    # Отклонить предложение обмена (POST)
    path('exchange/<int:pk>/decline/',
         ExchangeProposalDeclineView.as_view(), name='exchangeproposal_decline'),
]
