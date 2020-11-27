from dataclasses import field
from typing import ClassVar, List, Optional, Type
from decimal import Decimal

import marshmallow
import marshmallow_enum
from marshmallow_dataclass import dataclass

from entities import SkipNoneSchema
from billing.constants import Currency, PaypalIntent, PaypalGoodsCategory, PaypalUserAction, PaypalShippingPreference


@dataclass(order=True, base_schema=SkipNoneSchema)
class PaypalAmount:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    currency_code: Currency = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(Currency, by_value=True)
        }
    )
    value: str


@dataclass(order=True, base_schema=SkipNoneSchema)
class PaypalItem:
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
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    item_total: PaypalAmount
    shipping: Optional[PaypalAmount]
    tax_total: Optional[PaypalAmount]


@dataclass(order=True, base_schema=SkipNoneSchema)
class PaypalAmountWithBreakdown(PaypalAmount):
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    breakdown: Optional[PaypalBreakdown]


# @dataclass(order=True)
# class PaypalShippingInfo:
#     Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema
#
#     address: PaypalAddress


@dataclass(order=True, base_schema=SkipNoneSchema)
class PaypalPurchaseUnit:
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