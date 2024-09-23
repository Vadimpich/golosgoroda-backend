from django.urls import path

from votings import views

urlpatterns = [
    path(
        '',
        views.ObjectListView.as_view(),
        name='index'
    ),
    path(
        'object/<int:pk>/',
        views.ObjectDetailView.as_view(),
        name='object_detail'
    ),
    path(
        'votings',
        views.VotingListView.as_view(),
        name='votings_list'
    ),
    path(
        'voting/<int:pk>/',
        views.VotingDetailView.as_view(),
        name='voting_detail'
    ),
    path(
        'add_to_voting/<int:object_id>/',
        views.add_object_to_voting,
        name='add_object_to_voting'
    ),
    path(
        'delete_voting/<int:voting_id>/',
        views.delete_voting,
        name='delete_voting'
    ),
]
