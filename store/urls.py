from django.urls import path
from . import views

app_name = "store"
urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<slug>/', views.product_detail, name='product_detail'),
    path('shop/', views.shop, name='shop'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('delete_cart_item/', views.delete_cart_item, name='delete_cart_item'),
    path('create_order/', views.create_order, name='create_order'),
    path('checkout/<order_id>/', views.checkout, name='checkout'),
    path('coupon_apply/<order_id>/', views.coupon_apply, name='coupon_apply'),
    path('paypal_payment_verify/<order_id>/', views.paypal_payment_verify, name='paypal_payment_verify'),
    path('payment_status/<order_id>/', views.payment_status, name='payment_status'),
    path('razorpay_payment_verify/<order_id>/', views.razorpay_payment_verify, name='razorpay_payment_verify'),
]