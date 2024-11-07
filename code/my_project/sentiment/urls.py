from django.urls import path
from . import views

app_name = 'sentiment'

urlpatterns = [
    path('wordcloud/', views.generate_wordcloud, name='generate_wordcloud'),
]
