from django.urls import path
from . import views
from reports import views

app_name = "reports"


urlpatterns = [
    
    path('charts',views.charts  ,name='charts'),
  
]