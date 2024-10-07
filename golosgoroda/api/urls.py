from django.urls import path

from .views import (
    ObjectListAPIView, ObjectDetailAPIView, ObjectDraftAPIView,
    VotingListAPIView, VotingDetailAPIView, form_voting, moderate_voting,
    UserAPIView, UserDetailAPIView, auth_user, deauth_user, object_image
)

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
    path('users/register/', UserAPIView.as_view(),
         name='user-register'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(),
         name='user-edit'),
    path('users/auth', auth_user, ),
    path('users/logout/', deauth_user, ),
]
