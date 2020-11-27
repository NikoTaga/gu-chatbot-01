from dataclasses import field
from datetime import datetime
from typing import (ClassVar, List, Optional, Type, Dict, Any)

import marshmallow
import marshmallow_enum
from marshmallow_dataclass import dataclass

from entities import SkipNoneSchema
from billing.constants import StripeCurrency, StripePaymentMethod, StripeMode


@dataclass(order=True)
class StripeProductData:
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
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    price_data: StripePriceData
    quantity: int


@dataclass(order=True, base_schema=SkipNoneSchema)
class StripeCheckout:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    payment_method_types: List[str] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.List(
                marshmallow_enum.EnumField(StripePaymentMethod, by_value=True)
            )
        }
    )
    line_items: List[StripeItem] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.List(
                marshmallow.fields.Nested(StripeItem.Schema()),
                # for our purposes
                validate=marshmallow.validate.Length(max=1),
            )
        }
    )
    mode: StripeMode = field(
        default=StripeMode.PAYMENT,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(StripeMode, by_value=True)
        }
    )
    success_url: str = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    cancel_url: str = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )