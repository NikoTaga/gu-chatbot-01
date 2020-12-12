"""Модуль содержит менеджеры моделей магазина.

Методы модуля предназначены для совершения операций между ботом и базой данных магазина."""

from typing import Optional, List, Dict, Any, TYPE_CHECKING

from django.utils import timezone
from django.db import models
from django.forms.models import model_to_dict
from django.db.models.query import QuerySet

from bot.models import Chat
from common.constants import OrderStatus

if TYPE_CHECKING:
    from .models import Order


class CategoryManager(models.Manager):
    def get_categories(self, category_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Возвращает список категорий в формате словаря.

        Возможно указание родительской категории для выдачи подкатегорий."""

        categories_queryset = self.filter(parent_category_id=category_id)
        categories = [{'id': c.id, 'name': c.name, 'parent_category_id': c.parent_category_id,
                       'child_category_exists': c.child_categories.exists()} for c in categories_queryset]
        # ToDo: optimize existence check
        return categories

    def get_category_by_id(self, category_id: Optional[int]) -> Dict[str, Any]:
        category = self.filter(pk=category_id).first()
        result = {'id': category.id, 'name': category.name, 'parent_category_id': category.parent_category_id,
                  'child_category_exists': category.child_categories.exists()}

        return result


class ProductManager(models.Manager):
    def get_products(self, category_id: Optional[int]) -> List[Dict[str, Any]]:
        """Возвращает список товаров из категории."""

        products = list(self.filter(categories__id=category_id).values('id', 'name', 'categories', 'price',
                                                                       'image_url', 'description', 'is_active'))
        return products

    def get_product_by_id(self, product_id: Optional[int]) -> Dict[str, Any]:
        product = model_to_dict(self.get(id=product_id), fields=(('id', 'name', 'categories', 'price',
                                                                  'image_url', 'description', 'is_active')))
        return product

    def get_products_by_query(self, query_string: str) -> List[Dict[str, Any]]:
        """Возвращает список товаров, отфильтрованных поиском по подстроке наименования."""

        products = list(self.filter(name__icontains=query_string).values('id', 'name', 'price', 'image_url',
                                                                         'description', 'is_active'))
        return products


class OrderManager(models.Manager):
    def get_order(self, order_id: int) -> QuerySet:
        # ToDo: change return value and everything related
        return self.filter(id=order_id)

    def make_order(self,
                   chat_id_in_messenger: str,
                   bot_id: int,
                   product_id: Optional[int],
                   description: Optional[str] = '') -> 'Order':

        """Создаёт и возвращает заказ на основе требуемых параметров."""

        from .models import Product

        product = Product.objects.get_product_by_id(product_id)
        chat = Chat.objects.get(bot_id=bot_id, id_in_messenger=chat_id_in_messenger)
        order = self.create(chat=chat, product_id=product_id, total=product['price'], description=description)

        return order

    def update_order(self, order_id: int, status: int) -> None:
        """Обновляет статус заказа на завершённый или отменённый."""

        order = self.get_order(order_id).first()
        order.status = status
        if status == OrderStatus.CANCELED.value:
            order.cancel_date = timezone.now()
        elif status == OrderStatus.COMPLETE.value:
            order.paid_date = timezone.now()
        order.save()
        return order
