"""Содержит сущности для сериализации данных при обмене со Stripe."""

from dataclasses import field
from typing import (ClassVar, List, Optional, Type)

import marshmallow
import marshmallow_enum
from marshmallow_dataclass import dataclass

from common.entities import SkipNoneSchema
from billing.constants import StripeCurrency, StripePaymentMethod, StripeMode


@dataclass(order=True)
class StripeProductData:
    """Класс данных для хранения информации о свойствах позиции товара.

    Содержит наименование, описание и набор ссылок на изображения (при необходимости)"""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    name: str
    description: Optional[str]
    images: Optional[List[str]] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.List(
                marshmallow.fields.Url(allow_none=True)
            )
        }
    )


@dataclass(order=True)
class StripePriceData:
    """Класс данных для хранения информации о товаре и его цене."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    unit_amount: int
    product_data: StripeProductData
    currency: StripeCurrency = field(
        default=StripeCurrency.RUB,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(StripeCurrency, by_value=True)
        }
    )


@dataclass(order=True)
class StripeItem:
    """Класс данных для хранения информации о позиции в заказе (включая количество)."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    price_data: StripePriceData
    quantity: int


@dataclass(order=True, base_schema=SkipNoneSchema)
class StripeCheckout:
    """Класс данных верхнего уровня для хранения информации о запросе создания Payment.

    Используется для сериализации данных для исходящего запроса.
    Содержит намерение оплаты, наборы товаров из заказа, настройки для работы с покупателем
    и ссылки для перенаправления при удаче или неудаче оплаты.
    """

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    payment_method_types: List[StripePaymentMethod] = field(
        metadata={
            "marshmallow_field": marshmallow.fields.List(
                marshmallow_enum.EnumField(StripePaymentMethod, by_value=True)
            )
        }
    )
    line_items: List[StripeItem] = field(
        metadata={
            "marshmallow_field": marshmallow.fields.List(
                marshmallow.fields.Nested(StripeItem.Schema()),
                # for our purposes
                validate=marshmallow.validate.Length(max=1),
            )
        }
    )
    success_url: str = field(
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    cancel_url: str = field(
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    mode: StripeMode = field(
        default=StripeMode.PAYMENT,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(StripeMode, by_value=True)
        }
    )
