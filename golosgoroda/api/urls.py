from django.urls import path, include
from rest_framework import routers

from .views import (
    ObjectListAPIView, ObjectDetailAPIView, ObjectDraftAPIView,
    VotingListAPIView, VotingDetailAPIView, form_voting, moderate_voting,
    object_image, UserViewSet, login_view, logout_view
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Услуги
    path('objects/', ObjectListAPIView.as_view(), name='object-list'),
    path('objects/<int:pk>/', ObjectDetailAPIView.as_view(),
         name='object-detail'),
    path('objects/<int:pk>/draft/', ObjectDraftAPIView.as_view(),
         name='add-to-voting'),
    path('objects/<int:pk>/image/', object_image,
         name='change-image'),

    # Заявки
    path('votings/', VotingListAPIView.as_view(), name='voting-list'),
    path('votings/<int:pk>/', VotingDetailAPIView.as_view(),
         name='voting-detail'),
    path('votings/<int:pk>/form/', form_voting,
         name='form-voting'),
    path('votings/<int:pk>/moderate/', moderate_voting,
         name='moderate-voting'),

    # Пользователи
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', include(router.urls)),
]
