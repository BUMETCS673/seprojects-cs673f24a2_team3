from django.urls import path
from . import  views
from django.shortcuts import render


print("Loading URL patterns")

app_name = 'analysis'


urlpatterns = [
    path('', views.index, name='index'),  # Home page
    #path('login/', auth_views.LoginView.as_view(), name='login'),  # Login page
    path('dashboard/', views.dashboard_view, name='dashboard'),  # Dashboard page
    path('dashboard/paginated_movie_table/', views.paginated_movie_table, name='paginated_movie_table'), # handle the AJAX pagination view
    path('dashboard/get-top-production-companies/', views.get_top_production_companies, name='get_top_production_companies'), # handle Top bar update
    path('funnel-data/', views.funnel_data_api, name='funnel_data_api'), # for API test
    path('language_map/', views.language_map_view, name='language_map'), # for language map
    path('box_office/', views.box_office_view, name='box_office'),  # Box_Office page
    path('genre_insights/', views.genre_insights_view, name='genre_insights'),  # Genre_Insights page
    path('movie_runtime/', views.movie_runtime_view, name='movie_runtime'),  # Movie_Runtime page
    path('language_diversity/', views.language_diversity_view, name='language_diversity'),  # Language_Diversity page
    #path('word_cloud/', views.word_cloud_view, name='word_cloud'),  # Word_Cloud page
    #path('reviews_analysis/', views.reviews_analysis_view, name='reviews_analysis'),  # Reviews_Analysis page
    #path('trend_analysis/', views.trend_analysis_view, name='trend_analysis'),  # Trend_Analysis page
    #path('AI_reports/', views.AI_reports_view, name='AI_reports') # AI_reports page
    #path('AI_reports/', views.AI_reports_view, name='AI_reports') # AI_reports page
    path('test/', lambda request: render(request, 'analysis/base.html')),
    path('wordCloud/', views.word_cloud_page, name='wordCloud'),
    path('wordCloud/data/', views.word_cloud_view, name='wordCloudData'),
]

