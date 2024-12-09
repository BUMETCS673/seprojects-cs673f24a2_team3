from django.urls import path
from . import  views

print("Loading URL patterns")

app_name = 'users'


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('secure/', views.secure_view, name='secure_view'),
]