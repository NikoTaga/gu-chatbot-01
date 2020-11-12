# Create your views here.
from django.shortcuts import render


developers = (
    'Шадрин Николай Николаевич',
    'Шредер Юрий Вальтрович',
    'Сергеев Сергей Александрович',
    'Мельников Александр Валерьевич',
    'Чекунов Владислав Юрьевич',
    )

def index_page(request) -> render:
    context = {
        'title_page': 'Основная страница',
        'developers': developers,
        }

    return render(request, 'shop/index.html', context)
