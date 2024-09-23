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
        'name': 'Новая станция метро в районе Котельники',
        'image': get_image_url('golosgoroda', 'metro.png'),
        'info': 'Планируется открытие новой станции метро, которая улучшит транспортную доступность района и сократит время поездки до центра города.',
        'selected': True,
    },
    {
        'id': 2,
        'name': 'Новый ЖК от компании ПИК в районе Котельники',
        'image': get_image_url('golosgoroda', 'house2.jpg'),
        'info': 'Современный жилой комплекс с развитой инфраструктурой и комфортными условиями для жизни. Рядом строятся школы и детские сады.',
        'selected': True,
    },
    {
        'id': 3,
        'name': 'Автовокзал в районе Котельники',
        'image': get_image_url('golosgoroda', 'auto.jpg'),
        'info': 'Новый автовокзал обеспечит удобное сообщение между городом и пригородами, станет важным транспортным узлом района.',
        'selected': False,
    },
    {
        'id': 4,
        'name': 'ЖК от ГК Самолёт в районе Котельники',
        'image': get_image_url('golosgoroda', 'house.jpg'),
        'info': 'Строительство жилого комплекса от известного застройщика, предлагающего доступное жилье с хорошей планировкой и благоустройством территории.',
        'selected': False,
    },
]

SELECTED = [
    [
        {**VOTINGS[1], 'count': 40},
        {**VOTINGS[2], 'count': 50},
        {**VOTINGS[3], 'count': 100},
    ],
    [
        {**VOTINGS[0], 'count': 60},
        {**VOTINGS[2], 'count': 60},
        {**VOTINGS[3], 'count': 70},
    ],
    [
        {**VOTINGS[0], 'count': 10},
        {**VOTINGS[1], 'count': 15},
        {**VOTINGS[2], 'count': 20},
    ]
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


def object_detail(request, pk):
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
        'votings': SELECTED[pk]
    }
    return render(
        request,
        'votings/selected.html',
        context
    )
