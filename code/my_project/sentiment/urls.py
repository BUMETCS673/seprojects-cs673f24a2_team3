from django.urls import path
from . import  views

print("Loading URL patterns")

app_name = 'sentiment'


urlpatterns = [
    path('', views.index, name='index'),  # Home page
    
]

