from django.urls import path
from . import views
from userauths import views

app_name = "userauths"


urlpatterns = [
  path('sign-up/',views.register_view  ,name='sign-up'),
  path('sign-in/',views.login_view  ,name='sign-in'),
  path('sign-out/',views.logout_view  ,name='sign-out'),
  
  
  path('password_reset/', views.password_reset_request, name='password_reset_request'),
  path('password_reset/done/', views.password_reset_done, name='password_reset_done'),
  path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
  path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
]