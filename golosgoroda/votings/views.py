import os
from datetime import timedelta

from django.shortcuts import render
from minio import Minio

MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)


def get_image_url(bucket_name, object_name):
    return minio_client.presigned_get_object(bucket_name, object_name,
                                             expires=timedelta(hours=1))


VOTINGS = [
    {
        'id': 1,
        'name': 'Выбираем название для нового парка на Павелецкой Площади',
        'image': get_image_url('golosgoroda', 'park.png'),
        'info': 'Классный парк!',
        'selected': False,
    },
    {
        'id': 2,
        'name': 'Выбираем название для нового парка на Павелецкой Площади',
        'image': get_image_url('golosgoroda', 'park.png'),
        'info': 'Классный парк!',
        'selected': True,
    },
    {
        'id': 3,
        'name': 'Выбираем название для нового парка на Павелецкой Площади',
        'image': get_image_url('golosgoroda', 'park.png'),
        'info': 'Классный парк!',
        'selected': False,
    },
    {
        'id': 4,
        'name': 'Выбираем название для нового парка на Павелецкой Площади',
        'image': get_image_url('golosgoroda', 'park.png'),
        'info': 'Классный парк!',
        'selected': False,
    },
    {
        'id': 5,
        'name': 'Выбираем названия для статуи Медведя',
        'image': get_image_url('golosgoroda', 'medved.jpeg'),
        'info': 'Крутой медведь!',
        'selected': True,
    },
    {
        'id': 6,
        'name': 'Выбираем названия для статуи Медведя',
        'image': get_image_url('golosgoroda', 'medved.jpeg'),
        'info': 'Крутой медведь!',
        'selected': False,
    },
    {
        'id': 7,
        'name': 'Выбираем названия для статуи Медведя',
        'image': get_image_url('golosgoroda', 'medved.jpeg'),
        'info': 'Крутой медведь!',
        'selected': False,
    },
    {
        'id': 8,
        'name': 'Выбираем названия для статуи Медведя',
        'image': get_image_url('golosgoroda', 'medved.jpeg'),
        'info': 'Крутой медведь!',
        'selected': False,
    },
]


def index(request):
    object_name = request.GET.get('object_name', '')
    if object_name:
        votings = [
            x for x in VOTINGS if object_name.lower() in x['name'].lower()
        ]
    else:
        votings = VOTINGS
    context = {
        'votings': votings
    }
    return render(
        request,
        'votings/index.html',
        context
    )


def voting_detail(request, pk):
    context = {
        'voting': VOTINGS[int(pk) - 1]
    }
    return render(
        request,
        'votings/voting_detail.html',
        context
    )


def selected(request, pk):
    context = {
        'votings': [x for x in VOTINGS if x['selected']]
    }
    return render(
        request,
        'votings/selected.html',
        context
    )
