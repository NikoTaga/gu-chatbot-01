from django.contrib import admin

from .models import (Checkout)


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    """Класс с настройками для работы с моделью Checkout в админке Django."""

    readonly_fields = ('created_at', 'updated_at')
    list_display = ('id',
                    'order',
                    'system',
                    'status',
                    'tracking_id',
                    'capture_id',
                    )
    list_filter = ('system',)
    search_fields = ('id__exact', 'system__exact', 'tracking_id__exact')
