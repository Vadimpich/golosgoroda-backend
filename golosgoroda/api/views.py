import uuid

import redis
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from minio import Minio
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, authentication_classes, \
    permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from golosgoroda import settings
from users.permissions import IsAdmin, IsManager, IsAuthor
from votings.models import Object, Voting, VotingObject, User
from .serializers import (ObjectSerializer, VotingSerializer,
                          VotingObjectSerializer, UserSerializer,
                          VotingDetailSerializer, VotingEditSerializer)

# Connect to our Redis instance
session_storage = redis.StrictRedis(host=settings.REDIS_HOST,
                                    port=settings.REDIS_PORT)


def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)

        return decorated_func

    return decorator


class ObjectListAPIView(APIView):
    def get(self, request):
        user = request.user

        objects = Object.objects.filter(status='active')

        name = request.query_params.get('name', None)
        if name:
            objects = objects.filter(name__icontains=name)

        serializer_data = ObjectSerializer(objects, many=True).data

        if user.is_authenticated:
            draft = Voting.objects.filter(user=user, status='draft').first()
        else:
            draft = None
        response_data = {
            'draft_voting': draft.id if draft else None,
            'draft_count': VotingObject.objects.filter(
                object__in=objects, voting=draft
            ).count() if draft else 0,
            'data': serializer_data
        }

        return Response(response_data)

    @swagger_auto_schema(request_body=ObjectSerializer)
    @method_permission_classes((IsManager,))
    def post(self, request):
        data = request.data
        serializer = ObjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObjectDetailAPIView(APIView):
    def get(self, request, pk):
        obj = get_object_or_404(Object, pk=pk, status='active')
        serializer = ObjectSerializer(obj)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ObjectSerializer)
    @method_permission_classes((IsManager,))
    def put(self, request, pk):
        obj = get_object_or_404(Object, pk=pk, status='active')
        serializer = ObjectSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_permission_classes((IsAdmin,))
    def delete(self, request, pk):
        obj = get_object_or_404(Object, pk=pk, status='active')

        minio_client = Minio(
            settings.MINIO_STORAGE_ENDPOINT,
            access_key=settings.MINIO_STORAGE_ACCESS_KEY,
            secret_key=settings.MINIO_STORAGE_SECRET_KEY,
            secure=False
        )

        image_path = obj.image.url
        minio_client.remove_object(settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                                   image_path)

        obj.status = 'deleted'
        obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@permission_classes((IsAuthor,))
@api_view(['POST'])
def object_image(request, pk):
    image = request.data['image']
    obj = get_object_or_404(Object, pk=pk)
    if obj.status == 'deleted':
        return Response(
            {'error': 'Объект удалён.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    obj.image = image
    obj.save()
    return Response(ObjectSerializer(obj).data)


class ObjectDraftAPIView(APIView):
    def post(self, request, pk):
        user = request.user
        draft = Voting.objects.filter(user=user, status='draft').first()
        if not draft:
            draft = Voting(user=user, status='draft')
            draft.save()
        VotingObject(object_id=pk, voting_id=draft.id).save()
        return Response(status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        user = request.user
        draft = Voting.objects.filter(user=user, status='draft').first()
        if not draft:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        voting_object = get_object_or_404(VotingObject, object_id=pk,
                                          voting_id=draft.id)
        serializer = VotingObjectSerializer(voting_object, data=request.data,
                                            partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = request.user
        draft = Voting.objects.filter(user=user, status='draft').first()
        if not draft:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        voting_object = get_object_or_404(VotingObject, object_id=pk,
                                          voting_id=draft.id)
        voting_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VotingListAPIView(APIView):
    def get(self, request):
        user = request.user
        votings = Voting.objects.filter(user=user).exclude(
            status__in=['draft', 'deleted']
        )

        status = request.query_params.get('status', None)
        if status:
            votings = votings.filter(status=status)

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)

        if start_date:
            votings = votings.filter(formed_at__gte=start_date)

        if end_date:
            votings = votings.filter(formed_at__lte=end_date)

        serializer = VotingSerializer(votings, many=True)
        return Response(serializer.data)


class VotingDetailAPIView(APIView):
    def get(self, request, pk):
        voting = get_object_or_404(Voting, pk=pk)
        serializer = VotingDetailSerializer(voting)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=VotingDetailSerializer)
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
        if voting.status == 'deleted':
            return Response(
                {"error": "Заявка уже удалена"},
                status=status.HTTP_400_BAD_REQUEST
            )
        voting.status = 'deleted'
        voting.save()
        return Response(status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['Put'])
def form_voting(request, pk):
    user = request.user
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


@csrf_exempt
@api_view(['Put'])
def moderate_voting(request, pk):
    user = request.user
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


class UserViewSet(viewsets.ModelViewSet):
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    model_class = User

    @swagger_auto_schema(request_body=UserSerializer)
    def create(self, request):
        """
        Функция регистрации новых пользователей
        Если пользователя c указанным в request username ещё нет, в БД будет добавлен новый пользователь.
        """
        if self.model_class.objects.filter(
                username=request.data['username']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # print(serializer.data) - что это за строчка?!
            self.model_class.objects.create_user(
                username=request.data['username'],
                email=serializer.data['email'],
                password=serializer.data['password'],
                is_superuser=serializer.data['is_superuser'],
                is_staff=serializer.data['is_staff']
            )
            return Response({'status': 'Success'}, status=200)
        return Response(
            {'status': 'Error', 'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdmin | IsManager]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]



@authentication_classes([])
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data["username"]
    password = request.data["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, username)

        response = Response("{'status': 'ok'}")
        response.set_cookie("session_id", random_key)

        return response
    else:
        return Response("{'status': 'error', 'error': 'Login failed!'}")


@swagger_auto_schema(method='post')
def logout_view(request):
    logout(request._request)
    return Response({'status': 'Success'})
