from django.urls import path

from votings import views

urlpatterns = [
    path('', views.index, name='index'),
    path('objects/<int:pk>/', views.object_detail, name='object_detail'),
    path('selected/<int:pk>/', views.selected, name='selected'),
]
