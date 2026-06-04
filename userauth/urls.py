from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/submit-complaint/', views.submit_complaint, name='submit_complaint'),
    path('api/get-complaints/', views.get_complaints, name='get_complaints'),
    path('api/get-stats/', views.get_stats, name='get_stats'),
    path('api/get-profile/', views.get_user_profile, name='get_profile'),
    path('api/update-phone/', views.update_phone, name='update_phone'),
]