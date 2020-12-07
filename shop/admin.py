from django.contrib import admin

from .models import (Category, Product, Order)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Класс с настройками для работы с моделью Category в админке Django."""

    readonly_fields = ('created_at', 'updated_at')
    list_display = ('name', 'parent_category', 'is_active', 'sort_order')
    search_fields = ('name__exact',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Класс с настройками для работы с моделью Product в админке Django."""

    readonly_fields = ('created_at', 'updated_at')
    list_display = ('name', 'get_categories', 'price', 'description', 'image_url', 'is_active', 'sort_order')
    search_fields = ('name__exact', 'categories__name__exact')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Класс с настройками для работы с моделью Order в админке Django."""

    readonly_fields = ('created_at', 'updated_at')
    list_display = ('chat', 'description', 'product', 'total', 'status', 'paid_date', 'cancel_date')
    list_filter = ('product', 'status')
    search_fields = ('chat__exact',)
