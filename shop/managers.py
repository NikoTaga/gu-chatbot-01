from typing import Optional, List, Dict, Any
from decimal import Decimal

from django.utils import timezone
from django.db import models
from django.forms.models import model_to_dict
from django.db.models.query import QuerySet

from constants import OrderStatus


class CategoryManager(models.Manager):
    def get_categories(self, category_id: Optional[int] = None) -> List[Dict[str, Any]]:
        categories_queryset = self.filter(parent_category_id=category_id)
        categories = [{'id': c.id, 'name': c.name, 'parent_category_id': c.parent_category_id,
                       'child_category_exists': c.child_categories.exists()} for c in categories_queryset]
        # ToDo: optimize existence check
        return categories


class ProductManager(models.Manager):
    def get_products(self, category_id: int) -> List[Dict[str, Any]]:
        products = list(self.filter(categories__id=category_id).values('id', 'name', 'categories', 'price',
                                                                       'image_url', 'description', 'is_active'))
        return products

    def get_product_by_id(self, product_id: int) -> Dict[str, Any]:
        product = model_to_dict(self.get(id=product_id), fields=(('id', 'name', 'categories', 'price',
                                                                  'image_url', 'description', 'is_active')))
        return product

    def get_products_by_query(self, query_string: str) -> List[Dict[str, Any]]:
        products = list(self.filter(name__icontains=query_string).values('id', 'name', 'price', 'image_url',
                                                                         'description', 'is_active'))
        return products


class OrderManager(models.Manager):
    def get_order(self, order_id: int) -> QuerySet:
        return self.filter(id=order_id)

    def make_order(self, chat_id: int, product_id: int, price: Decimal, description: Optional[str] = '') -> None:
        self.create(chat_id=chat_id, product_id=product_id, total=price, description=description)

    def update_order(self, order_id: int, status: int) -> None:
        order = self.get_order(order_id)
        if status == OrderStatus.CANCELED.value:
            order.update(status=status, cancel_date=timezone.now())
        elif status == OrderStatus.COMPLETE.value:
            order.update(status=status, paid_date=timezone.now())
        else:
            order.update(status=status)