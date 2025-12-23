from django.urls import path
from . import views

app_name = 'data_management'

urlpatterns = [
    path('view/', views.view_all_data_view, name='view_all_data'),
    path('upload/', views.upload_data_view, name='upload_data'),
    path('upload/validate/', views.validate_upload_preview, name='validate_upload'),
    path('history/', views.upload_history_view, name='upload_history'),
    path('delete/', views.delete_data_view, name='delete_data'),
]
