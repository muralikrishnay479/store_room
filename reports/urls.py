from django.urls import path
from . import views
from reports import views

app_name = "reports"


urlpatterns = [
    
    path('charts',views.charts  ,name='charts'),
    path('donut',views.donut  ,name='donut'),
    path('data/', views.get_dashboard_data, name='dashboard-data'),
  
]