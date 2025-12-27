from django.urls import path
from . import views

app_name = 'data_management'

urlpatterns = [
    path('view/', views.view_all_data_view, name='view_all_data'),
    path('upload/', views.upload_data_view, name='upload_data'),
    path('upload/validate/', views.validate_upload_preview, name='validate_upload'),
    path('history/', views.upload_history_view, name='upload_history'),
    path('delete/', views.delete_data_view, name='delete_data'),
    
    # Komitmen routes
    path('komitmen/validate/', views.validate_komitmen_ajax, name='validate_komitmen'),  # AJAX validation
    path('komitmen/upload/', views.upload_komitmen, name='upload_komitmen'),
    path('komitmen/preview/', views.preview_komitmen, name='preview_komitmen'),
    path('komitmen/confirm/', views.confirm_komitmen_upload, name='confirm_komitmen'),
    path('komitmen/history/', views.komitmen_history, name='komitmen_history'),
    path('komitmen/delete/<int:upload_id>/', views.delete_komitmen, name='delete_komitmen'),
    path('komitmen/view/', views.view_komitmen, name='view_komitmen'),  # New: View komitmen data
    path('komitmen/update-cell/', views.update_komitmen_cell, name='update_komitmen_cell'),  # New: AJAX update
]
