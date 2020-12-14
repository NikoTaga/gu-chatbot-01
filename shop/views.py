# Create your views here.
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponse


developers = (
    'Чекунов Владислав Юрьевич',
    'Мельников Александр Валерьевич',
    'Сергеев Сергей Александрович',
    'Шадрин Николай Николаевич',
    'Шредер Юрий Вальтрович',
    )


def index_page(request: WSGIRequest) -> HttpResponse:
    """Вид главной страницы, содержит список разработчиков и виджет JivoSite."""

    context = {
        'title_page': 'Основная страница',
        'developers': developers,
    }

    return render(request, 'shop/index.html', context)
