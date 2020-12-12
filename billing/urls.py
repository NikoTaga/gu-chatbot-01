"""Модуль содержит список адресов страниц под управлением billing."""

from django.urls import path

import billing.views as billing


app_name = 'billing'

urlpatterns = [
    path('pp_webhook/', billing.paypal_webhook),
    path('stripe_webhook/', billing.stripe_webhook),
    path('stripe_redirect/<str:cid>', billing.stripe_redirect),
    path('stripe_success/<int:order_id>', billing.stripe_payment_success),
    # path('stripe_cancel/<int:order_id>', billing.stripe_payment_cancel),
]
