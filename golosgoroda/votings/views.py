from django.db import connection
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView

from .models import Object, Voting, VotingObject


class ObjectListView(ListView):
    model = Object
    template_name = 'votings/index.html'
    context_object_name = 'objects'

    def get_queryset(self):
        object_name = self.request.GET.get('object_name', '')
        queryset = Object.objects.filter(status='active')

        if object_name:
            queryset = queryset.filter(name__icontains=object_name)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        draft_voting = Voting.objects.filter(
            user=self.request.user, status='draft'
        ).first()

        objects_with_status = []

        if draft_voting:
            draft_voting_object_count = VotingObject.objects.filter(
                voting=draft_voting
            ).count()

            for obj in context['objects']:
                is_added = VotingObject.objects.filter(voting=draft_voting,
                                                       object=obj).exists()
                objects_with_status.append({
                    'object': obj,
                    'is_added': is_added
                })

            context['draft_voting_object_count'] = draft_voting_object_count
        else:
            context['draft_voting_object_count'] = 0

        context['draft_voting'] = draft_voting
        context['objects_with_status'] = objects_with_status

        return context


class ObjectDetailView(DetailView):
    model = Object
    template_name = 'votings/object_detail.html'
    context_object_name = 'object'


def add_object_to_voting(request, object_id):
    if request.method == 'POST':
        city_object = get_object_or_404(Object, id=object_id)
        voting, created = Voting.objects.get_or_create(
            user=request.user, status='draft',
            defaults={'title': 'Новое голосование'}
        )
        votingobject = VotingObject.objects.filter(object=city_object,
                                                   voting=voting).first()
        if votingobject:
            votingobject.delete()
        else:
            VotingObject.objects.create(
                voting=voting, object=city_object
            )
        return redirect('index')
    return HttpResponseForbidden()


class VotingDetailView(DetailView):
    model = Voting
    template_name = 'votings/voting_detail.html'
    context_object_name = 'voting'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voting_id = context['voting'].id

        voting = get_object_or_404(Voting, id=voting_id)
        related_objects = Object.objects.filter(votingobject__voting=voting)

        context['objects'] = related_objects
        return context


class VotingListView(ListView):
    model = Voting
    template_name = 'votings/votings.html'
    context_object_name = 'votings'

    def get_queryset(self):
        queryset = Voting.objects.exclude(status='deleted')
        return queryset


def delete_voting(request, voting_id):
    if request.method == 'POST':
        voting = get_object_or_404(Voting, id=voting_id)
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE votings_voting SET status = %s WHERE id = %s",
                ['deleted', voting.id])
        return redirect('index')
    return HttpResponseForbidden()
