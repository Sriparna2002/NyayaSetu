# lawyer/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lawyer_portal, name='lawyer_portal'),
    path('list/', views.lawyer_portal, name='lawyer_list'),  # ← নতুন লাইন যোগ করুন (alias)
    path('create/', views.create_lawyer_profile, name='create_lawyer_profile'),
    path('detail/<int:lawyer_id>/', views.lawyer_detail, name='lawyer_detail'),
]