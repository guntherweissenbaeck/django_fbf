from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('manual/', views.manual_report, name='manual_report'),
    path('automatic/', views.automatic_reports, name='automatic_reports'),
    path('automatic/create/', views.create_automatic_report, name='create_automatic_report'),
    path('automatic/<int:report_id>/edit/', views.edit_automatic_report, name='edit_automatic_report'),
    path('automatic/<int:report_id>/delete/', views.delete_automatic_report, name='delete_automatic_report'),
    path('logs/', views.report_logs, name='report_logs'),
]
