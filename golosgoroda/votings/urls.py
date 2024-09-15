from django.urls import path

from votings import views

urlpatterns = [
    path('', views.index, name='index'),
    path('votings/<int:pk>', views.voting_detail, name='voting_detail'),
    path('selected/<int:pk>', views.selected, name='selected'),
]
