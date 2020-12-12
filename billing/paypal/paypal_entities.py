"""Содержит сущности для сериализации данных при обмене с PayPal."""

from dataclasses import field
from typing import ClassVar, List, Optional, Type

import marshmallow
import marshmallow_enum
from marshmallow_dataclass import dataclass

from common.entities import SkipNoneSchema
from billing.constants import Currency, PaypalIntent, PaypalGoodsCategory, PaypalUserAction, PaypalShippingPreference


@dataclass(order=True, base_schema=SkipNoneSchema)
class PaypalAmount:
    """Класс данных для хранения информации о суммах денег в разных валютах."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    currency_code: Currency = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(Currency, by_value=True)
        }
    )
    value: str


@dataclass(order=True, base_schema=SkipNoneSchema)
class PaypalItem:
    """Класс данных для хранения информации о позиции товара.

    Включает имя, описание, стоимость, количество, а также категорию (digital или physical goods) и артикул."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    name: str
    quantity: int
    unit_amount: PaypalAmount
    description: Optional[str]
    sku: Optional[str]
    category: Optional[PaypalGoodsCategory] = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(PaypalGoodsCategory, by_value=True)
        }
    )


@dataclass(order=True, base_schema=SkipNoneSchema)
class PaypalBreakdown:
    """Класс данных для хранения развёрнутой информации о стоимости товара.

    Включает базовую стоимость, цену доставку и налоги."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    item_total: PaypalAmount
    shipping: Optional[PaypalAmount]
    tax_total: Optional[PaypalAmount]


@dataclass(order=True, base_schema=SkipNoneSchema)
class PaypalAmountWithBreakdown(PaypalAmount):
    """Класс данных для обёртывания breakdown."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    breakdown: Optional[PaypalBreakdown]


# @dataclass(order=True)
# class PaypalShippingInfo:
#     Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema
#
#     address: PaypalAddress


@dataclass(order=True, base_schema=SkipNoneSchema)
class PaypalPurchaseUnit:
    """Класс данных для хранения информации об отдельном наборе товаров в заказе."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    amount: PaypalAmountWithBreakdown
    reference_id: Optional[str]
    description: Optional[str]
    invoice_id: Optional[str]
    custom_id: Optional[str]
    items: Optional[List[PaypalItem]] = field(
        metadata={
            "marshmallow_field": marshmallow.fields.List(
                marshmallow.fields.Nested(PaypalItem.Schema())
            )
        }
    )
    # shipping: Optional[PaypalShippingInfo]


@dataclass(order=True, base_schema=SkipNoneSchema)
class PaypalAppContext:
    """Класс данных для хранения информации о настройках для работы с покупателем.

    Содержит настройки получения предпочтительного адреса доставки и особенностей оплаты."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    shipping_preference: PaypalShippingPreference = field(
        default=PaypalShippingPreference.GET_FROM_FILE,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(PaypalShippingPreference, by_value=True)
        }
    )
    user_action: PaypalUserAction = field(
        default=PaypalUserAction.PAY_NOW,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(PaypalUserAction, by_value=True)
        }
    )


@dataclass(order=True, base_schema=SkipNoneSchema)
class PaypalCheckout:
    """Класс данных верхнего уровня для хранения информации о запросе Checkout.

    Используется для сериализации данных для исходящего запроса.
    Содержит намерение чекаута, наборы товаров из заказа и настройки работы с покупателем.
    """

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    intent: PaypalIntent = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(PaypalIntent, by_value=True)
        }
    )
    purchase_units: List[PaypalPurchaseUnit] = field(
        metadata={
            "marshmallow_field": marshmallow.fields.List(
                marshmallow.fields.Nested(PaypalPurchaseUnit.Schema()),
            )
        }
    )
    application_context: Optional[PaypalAppContext]
