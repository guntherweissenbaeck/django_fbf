from django.urls import path
from . import views

app_name = 'notizen'

urlpatterns = [
    # Main note views
    path('', views.notizen_list, name='list'),
    path('neu/', views.notiz_create, name='create'),
    path('<int:pk>/', views.notiz_detail, name='detail'),
    path('<int:pk>/bearbeiten/', views.notiz_edit, name='edit'),
    path('<int:pk>/loeschen/', views.notiz_delete, name='delete'),
    path('public/<uuid:token>/', views.notiz_public_edit, name='public_edit'),
    
    # Object attachment views
    path('anhaengen/<int:content_type_id>/<str:object_id>/', views.attach_notiz, name='attach'),
    path('objekt/<int:content_type_id>/<str:object_id>/', views.object_notizen, name='object_notizen'),
    
    # Page attachment views
    path('seite/<str:page_identifier>/anhaengen/', views.attach_page_notiz, name='attach_page'),
]
