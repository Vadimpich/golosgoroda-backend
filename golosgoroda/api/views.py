from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from votings.models import Object, Voting, VotingObject, User
from .serializers import (ObjectSerializer, VotingSerializer,
                          VotingObjectSerializer, UserSerializer,
                          VotingDetailSerializer, VotingEditSerializer)

USER_ID = 1


def get_const_user():
    return User.objects.get(pk=USER_ID)


class ObjectListAPIView(APIView):
    def get(self, request):
        user = get_const_user()
        objects = Object.objects.filter(status='active')

        name = request.query_params.get('name', None)
        if name:
            objects = objects.filter(name__icontains=name)

        serializer_data = ObjectSerializer(objects, many=True).data

        for obj in range(len(objects)):
            draft = Voting.objects.filter(user=user, status='draft').first()
            serializer_data[obj]['draft_id'] = (
                draft.id
                if draft and VotingObject.objects.filter(
                    object=serializer_data[obj]['id'], voting=draft.id)
                else None
            )

        return Response(serializer_data)

    def post(self, request):
        data = request.data
        serializer = ObjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObjectDetailAPIView(APIView):
    def get(self, request, pk):
        service = get_object_or_404(Object, pk=pk, status='active')
        serializer = ObjectSerializer(service)
        return Response(serializer.data)

    def put(self, request, pk):
        service = get_object_or_404(Object, pk=pk, status='active')
        serializer = ObjectSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        service = get_object_or_404(Object, pk=pk, status='active')
        service.status = 'deleted'
        service.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ObjectCartAPIView(APIView):
    def post(self, request, pk):
        user = get_const_user()
        draft = Voting.objects.filter(user=user, status='draft').first()
        if not draft:
            draft = Voting(user=user, status='draft')
            draft.save()
        VotingObject(object=pk, voting=draft.id).save()
        return Response(status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        user = get_const_user()
        draft = Voting.objects.filter(user=user, status='draft').first()
        if not draft:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        voting_object = get_object_or_404(VotingObject, object=pk,
                                          voting=draft.id)
        serializer = VotingObjectSerializer(voting_object, data=request.data,
                                            partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_const_user()
        draft = Voting.objects.filter(user=user, status='draft').first()
        if not draft:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        voting_object = get_object_or_404(VotingObject, object=pk,
                                          voting=draft.id)
        voting_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VotingListAPIView(APIView):
    def get(self, request):
        user = get_const_user()
        votings = Voting.objects.filter(user=user).exclude(
            status__in=['draft', 'deleted']
        )

        status = request.query_params.get('status', None)
        if status:
            votings = votings.filter(status=status)

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        if start_date:
            votings = votings.filter(created_at__gte=start_date)

        if end_date:
            votings = votings.filter(created_at__lte=end_date)

        serializer = VotingSerializer(votings, many=True)
        return Response(serializer.data)


class VotingDetailAPIView(APIView):
    def get(self, request, pk):
        voting = get_object_or_404(Voting, pk=pk)
        serializer = VotingDetailSerializer(voting)
        return Response(serializer.data)

    def put(self, request, pk):
        voting = get_object_or_404(Voting, pk=pk)
        serializer = VotingEditSerializer(voting, data=request.data,
                                          partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        voting = get_object_or_404(Voting, pk=pk)
        voting.status = 'deleted'
        voting.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['Put'])
def form_voting(request, pk):
    user = get_const_user()
    voting = get_object_or_404(Voting, pk=pk, user=user)

    if voting.status != 'draft':
        return Response(
            {"error": "Заявка уже сформирована или завершена"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not voting.title or not voting.voting_date:
        return Response(
            {"error": "Невозможно сформировать заявку без названия и даты"},
            status=status.HTTP_400_BAD_REQUEST
        )

    voting.status = 'formed'
    voting.formed_at = timezone.now()
    voting.save()
    return Response(VotingSerializer(voting).data)


@api_view(['Put'])
def moderate_voting(request, pk):
    user = get_const_user()
    voting = get_object_or_404(Voting, pk=pk)

    if voting.status not in ['formed']:
        return Response({
            "error": "Заявка не может быть завершена или отклонена, так как ее статус: " + voting.get_status_display()},
            status=status.HTTP_400_BAD_REQUEST)

    if 'action' not in request.data:
        return Response({"error": "Не передано действие"},
                        status=status.HTTP_400_BAD_REQUEST)

    action = request.data.get('action')
    if action not in ['complete', 'reject']:
        return Response({
            "error": "Некорректное действие: должно быть 'complete' или 'reject'"},
            status=status.HTTP_400_BAD_REQUEST)

    if action == 'complete':
        voting.status = 'completed'
        total_votes = VotingObject.objects.filter(voting=voting).aggregate(
            total_votes=models.Sum('votes_count'))['total_votes'] or 0
        voting.total_votes = total_votes
    else:
        voting.status = 'rejected'

    voting.moderator = user
    voting.completed_at = timezone.now()
    voting.save()
    return Response(VotingSerializer(voting).data, status=status.HTTP_200_OK)


class VotingObjectList(APIView):
    def get(self, request):
        voting_objects = VotingObject.objects.all()
        serializer = VotingObjectSerializer(voting_objects, many=True)
        return Response(serializer.data)


class UserAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailAPIView(APIView):
    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def auth_user(request):
    return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['POST'])
def deauth_user(request):
    return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
