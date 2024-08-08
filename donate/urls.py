from django.urls import path, include
from donate import views

urlpatterns = [

    path('paypal/', include("paypal.standard.ipn.urls")),
    path('payment_done/',views.payment_done, name='payment_done'),
    path('payment-cancelled/',views.payment_cancelled, name='payment_cancelled'),
    path("", views.home, name='home'),
]
