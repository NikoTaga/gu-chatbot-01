"""Модуль содержит описания моделей базы данных, применяющихся в billing."""

from django.db import models

from bot.models import TrackableUpdateCreateModel
from common.constants import PaymentSystem
from .managers import CheckoutManager


class Checkout(TrackableUpdateCreateModel):
    """Модель для описания проводимого процесса оплаты.

    Содержит поля для сопоставления с заказом, указания платёжной системы,
    идентификации операций и текущего статуса."""

    order = models.ForeignKey(
        'shop.Order',
        verbose_name='Order',
        # todo обдумать поведение
        on_delete=models.RESTRICT,
    )
    system = models.IntegerField('Billing system', choices=PaymentSystem.choices())
    tracking_id = models.CharField('Tracking id', max_length=255)
    capture_id = models.CharField('Capture id', max_length=255, null=True, blank=True)
    status = models.CharField(
        'Status',
        max_length=200,
        null=True,
        blank=True
    )
    objects = CheckoutManager()

    class Meta:
        verbose_name = 'Checkout'
        verbose_name_plural = 'Checkouts'
        app_label = 'billing'
        ordering = ['-created_at']
