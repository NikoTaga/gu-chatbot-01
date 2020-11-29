from django.urls import path

import billing.views as billing


app_name = 'billing'

urlpatterns = [
    path('pp_webhook/', billing.paypal_webhook),
    path('stripe_webhook/', billing.stripe_webhook),
    path('stripe_redirect/<str:cid>', billing.stripe_redirect),
    path('payment_success/<int:order_id>', billing.stripe_payment_success),
    # path('payment_cancel/', billing.stripe_payment_cancel),
]
