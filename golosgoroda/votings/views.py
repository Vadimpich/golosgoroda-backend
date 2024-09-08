from django.shortcuts import render

VOTINGS = [
    {
        'id': 1,
        'name': 'Выбираем название для нового парка на Павелецкой Площади',
        'image': 'https://localhost:9000/park.jpg',
        'info': 'Классный парк!'
    },
    {
        'id': 2,
        'name': 'Выбираем название для нового парка на Павелецкой Площади',
        'image': 'https://localhost:9000/park.jpg',
        'info': 'Классный парк!'
    },
    {
        'id': 3,
        'name': 'Выбираем название для нового парка на Павелецкой Площади',
        'image': 'https://localhost:9000/park.jpg',
        'info': 'Классный парк!'
    },
    {
        'id': 4,
        'name': 'Выбираем название для нового парка на Павелецкой Площади',
        'image': 'https://localhost:9000/park.jpg',
        'info': 'Классный парк!'
    },
]


def index(request):
    context = {
        'votings': VOTINGS
    }
    return render(request, 'index.html', context)


def voting(request, pk):
    return render(
        request,
        'vote.html',
        {'data': VOTINGS[int(pk) - 1]}
    )


def selected(request):
    return render(
        request,
        'selected.html'
    )
