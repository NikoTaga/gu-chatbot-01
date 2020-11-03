from django.db import models
from djmoney.models.fields import MoneyField

from bot.models import TrackableUpdateCreateModel
from constants import OrderStatus


class Category(TrackableUpdateCreateModel):
    parent_category = models.ForeignKey(
        'shop.Category',
        verbose_name='Parent category',
        blank=True,
        null=True,
        db_index=True,
        on_delete=models.SET_NULL,
        related_name='child_categories',
        related_query_name='child_category',
    )
    name = models.CharField('Name', max_length=100)
    is_active = models.BooleanField('Active', default=True)
    sort_order = models.PositiveIntegerField('Sort order', default=1)

    def __str__(self) -> str:
        if self.parent_category_id is not None:
            return '{parent_category} -> {category}'.format(parent_category=self.parent_category,
                                                            category=self.name)
        else:
            return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        app_label = 'shop'
        ordering = ['sort_order', 'name']


class Product(TrackableUpdateCreateModel):
    categories = models.ManyToManyField(
        Category,
        verbose_name='Categories',
        blank=True,
        related_name='categories',
    )
    name = models.CharField('Name', max_length=100, db_index=True)
    price = MoneyField('Price', max_digits=10, decimal_places=2, blank=True, default=0.0, default_currency='RUB')
    image_url = models.URLField('Image', max_length=2047, blank=True, null=True)
    description = models.TextField('Description', blank=True, default='')
    is_active = models.BooleanField('Active', default=True)
    sort_order = models.PositiveIntegerField('Sort order', default=1)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        app_label = 'shop'
        ordering = ['sort_order', 'name']


class Order(TrackableUpdateCreateModel):
    chat = models.ForeignKey(
        'bot.Chat',
        verbose_name='Chat',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    description = models.TextField('Comment', default='')
    product = models.ForeignKey(Product, verbose_name='Product', on_delete=models.CASCADE)
    total = MoneyField('Total', max_digits=10, decimal_places=2)

    status = models.IntegerField('Status', choices=OrderStatus.choices(), default=OrderStatus.NEW.value)
    paid_date = models.DateTimeField('Paid date', null=True, blank=True)
    cancel_date = models.DateTimeField('Cancel date', null=True, blank=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        app_label = 'shop'
        ordering = ['-created_at']
