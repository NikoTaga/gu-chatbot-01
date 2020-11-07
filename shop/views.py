# Create your views here.
from django.shortcuts import render


def index_page(request):
    context = {
        "title_page": 'Основная страница',
    }

    return render(request, 'shop/index.html', context)
