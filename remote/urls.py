from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('api/register/', views.api_register_device, name='api_register_device'),
    path('api/devices/', views.api_device_list, name='api_device_list'),
    path('api/command/send/', views.api_send_command, name='api_send_command'),
    path('api/logs/<int:device_id>/', views.api_terminal_logs, name='api_terminal_logs'),
    
    # === C++ client uchun eski polling URL'ini qaytarish (404 yo'qolishi uchun) ===
    path('api/client/<str:token>/poll/', views.client_poll, name='client_poll'),
    path('api/client/<str:token>/response/', views.client_response, name='client_response'),
]