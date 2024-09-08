from django.urls import path, include

from votings import views

urlpatterns = [
    path('', views.index, name='index'),
    path('votings/<int:pk>', views.voting, name='voting_detail'),
    path('selected/', views.selected, name='selected'),
]
