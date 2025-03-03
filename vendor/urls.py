from django.urls import path
from . import views


app_name = 'vendor'


urlpatterns = [
  path('reports/',views.reports  ,name='reports'),
  path( "", views.dashboard , name="vendor_dashboard"),
  path( "products/",views.products , name="products"),
  path( "orders/",views.orders , name="orders"),
  path( "order_details/<order_id>/",views.order_details, name="order_details"),
  path( "order_item_detail/<order_id>/item_id/",views.order_item_detail , name="order_item_detail"),
  path( "update_order_item_status/<order_id>/item_id/",views.update_order_item_status , name="update_order_item_status"),
  path( "update_order_status/<order_id>/",views.update_order_status , name="update_order_status"),
  # path( "products/", views.products , name="products"),
  
  
  path("coupons/", views.coupons, name="coupons"),
  path("coupons/<int:id>/", views.update_coupon, name="update_coupon"),
  path("create_coupon/", views.create_coupon, name="create_coupon"),
  path("delete_coupon/<int:id>/", views.delete_coupon, name="delete_coupon"),
  
  # path("update_review/<int:id>/", views.update_review, name="update_review"),
  
  path("reviews/", views.reviews, name="reviews"),
  path("update_replay/<int:id>/", views.update_replay, name="update_replay"),
  
  path("notis/", views.notis, name="notis"),
  path("mark_noti_seen/<int:id>/", views.mark_noti_seen, name="mark_noti_seen"),
  
    
  path("profile/", views.profile, name="profile"),
  path("change_password/", views.change_password, name="change_password"),
  path("create_product/", views.create_product, name="create_product"),
  
  path("create_product/", views.create_product, name="create_product"),
  path("update_product/<int:id>/", views.update_product, name="update_product"),
  path("delete_product/<product_id>/", views.delete_product, name="delete_product"),
  path("delete_variant/<int:product_id>/<int:variant_id>/", views.delete_variant, name="delete_variant"),
  path("delete_variant_item/<int:product_id>/<int:variant_id>/<int:item_id>/", views.delete_variant_item, name="delete_variant_item"),
  path("delete_gallery_image/<int:image_id>/", views.delete_gallery_image, name="delete_gallery_image"),
  
  

  path("get_product_data/", views.get_product_data, name="get_product_data"),
  path('get_review_data/', views.get_review_data, name='get_review_data'),
  path('get_order_payment_data/', views.get_order_payment_data, name='get_order_payment_data'),
  path('get_sales_data/', views.get_sales_data, name='get_sales_data'),
  
  
  path('api/vendor-data/', views.vendor_data_for_powerbi, name='vendor_data_for_powerbi'),
  path('api/all-data/', views.all_data_for_powerbi, name='all_data_for_powerbi'),

]