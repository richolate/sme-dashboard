from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('os/', views.dashboard_os_view, name='dashboard_os'),
    path('summary/', views.dashboard_summary_view, name='dashboard_summary'),
    path('grafik-harian/', views.dashboard_grafik_harian_view, name='dashboard_grafik_harian'),
    path('page/<slug:slug>/', views.metric_page_view, name='metric_page'),
]
