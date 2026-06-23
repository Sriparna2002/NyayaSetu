# adminauth/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Auth URLs
    path('login/', views.admin_login, name='admin_login'),
    path('register/', views.admin_register, name='admin_register'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.admin_logout, name='admin_logout'),
    
    # Admin Lawyer Management URLs - এই অংশটি যোগ করুন
    path('lawyers/', views.admin_lawyer_list, name='admin_lawyer_list'),
    path('lawyer/verify/<int:lawyer_id>/', views.admin_lawyer_verify, name='admin_lawyer_verify'),
    path('lawyer/delete/<int:lawyer_id>/', views.admin_lawyer_delete, name='admin_lawyer_delete'),
    
    # API URLs
    path('api/complaints/', views.get_all_complaints, name='admin_api_complaints'),
    path('api/update-status/', views.update_complaint_status, name='admin_api_update_status'),
    path('api/assign-officer/', views.assign_officer, name='admin_api_assign_officer'),
    path('api/stats/', views.get_admin_stats, name='admin_api_stats'),
    path('api/officers/', views.get_officers, name='admin_api_officers'),
    path('api/complaint/<str:complaint_id>/', views.get_complaint_detail, name='admin_complaint_detail'),
    path('forgot-password/', views.admin_forgot_password, name='admin_forgot_password'),
    path('reset-password/<uuid:token>/', views.admin_reset_password, name='admin_reset_password'),
]