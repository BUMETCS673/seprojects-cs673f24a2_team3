from django.urls import path
from . import views

app_name = 'sentiment'

print("Loading URL patterns")

urlpatterns = [
    path('', views.index, name='index'),  # Home page
    path('wordcloud/', views.generate_wordcloud, name='generate_wordcloud'),  # Word Cloud page
]
