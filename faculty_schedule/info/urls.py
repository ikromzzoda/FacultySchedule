from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('profile/', views.get_profile_info, name='get_profile_info'),
]
