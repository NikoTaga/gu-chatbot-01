# Create your views here.
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponse


developers = (
    'Шадрин Николай Николаевич',
    'Шредер Юрий Вальтрович',
    'Сергеев Сергей Александрович',
    'Мельников Александр Валерьевич',
    'Чекунов Владислав Юрьевич',
    )

def index_page(request: WSGIRequest)-> HttpResponse:
    context = {
        'title_page': 'Основная страница',
        'developers': developers,
        }
    print(type(request))
    print(type(render(request, 'shop/index.html', context)))
    return render(request, 'shop/index.html', context)
