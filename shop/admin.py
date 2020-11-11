from django.contrib import admin

from .models import (Category, Product, Order)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('name', 'parent_category', 'is_active', 'sort_order')
    search_fields = ('name__exact',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('name', 'price', 'description', 'image_url', 'is_active', 'sort_order')
    search_fields = ('name__exact',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('chat', 'description', 'product', 'total', 'status', 'paid_date', 'cancel_date')
    list_filter = ('product', 'status')
    search_fields = ('chat__exact',)
