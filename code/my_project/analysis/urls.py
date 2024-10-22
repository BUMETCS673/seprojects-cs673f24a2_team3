from django.urls import path
from . import  views


app_name = 'analysis'


urlpatterns = [
    path('', views.index, name='index'),  # Home page
    #path('data/', views.data_view, name='data'),  # Data page
    #path('movie_analysis/', views.analysis_view, name='movie_analysis'),  # Movie_Analysis page
]