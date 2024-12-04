from django.urls import path
from . import  views


app_name = 'analysis'


urlpatterns = [
    path('', views.index, name='index'),  # Home page
    #path('data/', views.data_view, name='data'),  # Data page
    #path('movie_analysis/', views.analysis_view, name='movie_analysis'),  # Movie_Analysis page
]

from django.urls import path
from .views import signup, CustomLoginView, home
from django.contrib.auth.views import LogoutView

urlpatterns += [
    path('signup/', signup, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('home/', home, name='home'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
