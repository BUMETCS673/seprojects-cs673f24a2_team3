from django.shortcuts import render
# from imdb import IMDb
# Create your views here.
from django.contrib import admin
from django.urls import path,include
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.core import serializers 
import json
from django.db import connection
from django.core.paginator import Paginator
from django.template.loader import render_to_string
import re
from .models import Movie
import pandas as pd  
import pymysql

def index(request):
    """
    View function for the home page of the site.
    """
    # Context data to pass to the template, such as any necessary information for rendering
    context = {
        'page_title': 'Movie Data Visualizations Platform',
        'message': 'Welcome to the Movie Data Visualizations Platform!',
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'analysis/index.html', context)


# def fetch_data_from_db():
#     """Fetches all movie data from the database using Django's connection."""
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT * FROM data")
#         rows = cursor.fetchall()
#         columns = [col[0] for col in cursor.description]
#         return pd.DataFrame(rows, columns=columns)

def fetch_movie_data():
    movies = Movie.objects.all().values('title', 'year', 'score', 'awards', 'type','gross','production_company','production_country','url','ontime')
    return pd.DataFrame(list(movies))

df = fetch_movie_data() # make df as global 


def process_movie_distribution_by_year_intervals(df):
    """Process movie distribution data into year intervals."""
    range_step = 5
    start_year = 1921
    end_year = 2022
    year_ranges = list(range(start_year, end_year + 1, range_step))
    categorized = pd.cut(df['year'], year_ranges, right=False)
    counts = categorized.value_counts().sort_index()

    year_labels = [f'[{start}, {end})' for start, end in zip(year_ranges[:-1], year_ranges[1:])]
    data = list(zip(counts.values.tolist(), year_labels))
    
    return [{'value': value, 'name': name} for value, name in data]

def process_language_data(df):
    """Extract and count languages from the dataset."""
    if 'language' in df.columns:
        languages = df['language'].str.split(' ').explode().replace('', pd.NA).dropna()
        counts = languages.value_counts().sort_index(ascending=False).head(20)
        return counts.index.tolist(), counts.tolist()
    else:
        return [], []

def process_movie_genres(df):
    """Process movie genres from the 'type' column and return their counts."""
    if 'type' in df.columns:
        genres = df['type'].str.split(',').explode().str.strip()
        counts = genres.value_counts().sort_index(ascending=False).head(20)
        return counts.index.tolist(), counts.tolist()
    else:
        return [], []

def process_top_production_companies(df,topN):
    """Process and return top production companies with split and count."""
    if 'production_company' in df.columns:
        # Split production companies by a comma delimiter
        companies = df['production_company'].str.split(',').explode().str.strip()
        # Count each company and sort by the highest counts
        company_counts = companies.value_counts().head(topN)
        
        # Prepare data for the chart
        data = [{"name": company, "value": count} for company, count in company_counts.items()]
        return data
    else:
        return []

def get_top_production_companies(request):
    """API endpoint to get top production companies based on selected topN."""
    df = fetch_movie_data() 
    topN = int(request.GET.get('topN', 10))  # Default to top 10 if not specified
    data = process_top_production_companies(df, topN)
    print (f"DEBUG: Requested page number from URL: {topN}") # debug line
    return JsonResponse({"data": data})

def process_award_bubble_data(df):
    """Process data for a bubble plot comparing movie ratings and the number of awards, including the title."""
    
    # Ensure required columns exist in the DataFrame
    if 'score' not in df.columns or 'awards' not in df.columns or 'title' not in df.columns or 'type' not in df.columns:
        raise ValueError("DataFrame must contain 'score', 'awards', 'title', and 'type' columns.")

    # Define a function to extract only the count of Oscars and BAFTAs won
    def count_specific_awards(awards_text):
        if pd.notnull(awards_text):
            oscars = re.search(r"(\d+) Oscar", awards_text)
            baftas = re.search(r"(\d+) BAFTA", awards_text)
            return (int(oscars.group(1)) if oscars else 0) + (int(baftas.group(1)) if baftas else 0)
        return 0

    df['awardCount'] = df['awards'].apply(count_specific_awards)

    # Prepare data for the bubble plot
    bubble_data = []
    for _, row in df.iterrows():
        bubble_data.append({
            "rating": row['score'],         # Movie rating
            "awards": row['awardCount'],    # Number of specific awards (Oscars + BAFTAs)
            "gross": row['gross'],          # Gross revenue
            "title": row['title'],          # Movie title for tooltip
            "awardType": 'Oscar' if row['awards'] and 'Oscar' in row['awards'] else 'BAFTA' if row['awards'] and 'BAFTA' in row['awards'] else "None" # Award type for color coding
        })

    return bubble_data

def process_nested_rating_distribution(df):
    # Inner data: Get the top 3 genres across all movies
    top_genres = df['type'].str.split(',').explode().str.strip().value_counts().head(3)
    inner_data = [{'value': count, 'name': genre} for genre, count in top_genres.items()]

    # Outer data: Count movies by rating, sorted in ascending numerical order
    rating_counts = df['score'].value_counts().items()
    outer_data = [{'value': count, 'name': f'Rating {rating}'} for rating, count in sorted(rating_counts, key=lambda x: float(x[0]))]

    return {'inner': inner_data, 'outer': outer_data}


# Process data for funnel chart showing number of movies produced by country
def process_funnel_data(df):
    # Split countries by comma, remove extra whitespace, and explode into individual rows
    df['production_country'] = df['production_country'].str.split(',')
    country_counts = df.explode('production_country')  # Separate each country into its own row
    country_counts['production_country'] = country_counts['production_country'].str.strip()  # Remove any extra whitespace

    # Count movies by production country and take the top 10
    country_counts = country_counts['production_country'].value_counts().head(10)
    funnel_data = [{'name': country, 'value': count} for country, count in country_counts.items()]
    return funnel_data

def paginated_movie_table(request):
    # Fetch data for the table
    df = fetch_movie_data()
    table_data = df[['title', 'url', 'year', 'ontime', 'score']].to_dict(orient='records')

    # Set up pagination
    paginator = Paginator(table_data, 10)  # Show 10 movies per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Render the HTML for the table's body only
    table_html = render_to_string('analysis/partials/movie_table.html', {'page_obj': page_obj})
    return JsonResponse({'table_html': table_html})

def dashboard_view(request):
    df = fetch_movie_data()       

    # Select specific columns for the table display, in the desired order
    table_data = df[['title', 'url', 'year', 'ontime', 'score']].to_dict(orient='records')
    
    # Implement pagination
    page_number = request.GET.get("page")
    
    print(f"DEBUG: Requested page number from URL: {page_number}")  # New debug line
    paginator = Paginator(table_data, 10)  # Paginate the table data
    page_obj = paginator.get_page(page_number)

    # Debugging the actual page object state
    print(f"DEBUG: Current page number in view: {page_obj.number}")

    page_obj = paginator.get_page(page_number)
     
   # Construct pagination HTML
   # Start by initializing pagination_html as an empty string
   # Construct simplified pagination HTML
   # Construct pagination HTML
    pagination_html = '<ul class="pagination pagination-sm mb-0 d-flex justify-content-center">'
    
    # Debugging statement to print current and next page numbers
    # print(f"DEBUG: Current page number: {page_obj.number}")
    # Debug current and next page number
    print(f"DEBUG: Current page number: {page_obj.number}")
 

# Check if the request is AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        table_html = render_to_string("analysis/partials/movie_table.html", {"page_obj": page_obj})
        pagination_html = render_to_string("analysis/partials/pagination.html", {"page_obj": page_obj})
        return JsonResponse({"html": table_html, "pagination_html": pagination_html})

    # Process various visual data
    movie_distribution_by_year_intervals = process_movie_distribution_by_year_intervals(df)
    languages, language_counts = process_language_data(df)
    genres, genre_counts = process_movie_genres(df)
    top_companies = process_top_production_companies(df,10)
    award_bubble_data = process_award_bubble_data(df)
    rating_distribution = process_nested_rating_distribution(df) 
    funnel_data = process_funnel_data(df)
    
    context = {
        'movie_distribution_by_year_intervals': json.dumps(movie_distribution_by_year_intervals),
        'languages': json.dumps(languages),
        'language_counts': json.dumps(language_counts),
        'movie_genres': json.dumps(genres),
        'genre_counts': json.dumps(genre_counts),
        'top_companies': json.dumps(top_companies),
        'award_bubble_data': json.dumps(award_bubble_data),
        'rating_distribution': json.dumps(rating_distribution), 
        'funnel_data': json.dumps(funnel_data),
        'page_obj': page_obj,  # Pass paginated movies data to the template
    }

    return render(request, 'analysis/dashboard.html', context)



# def movie_runtime_view(request):
    # df = fetch_data_from_db()

    # # Process various visual data
    # movie_data = process_movie_runtime(df)
    # languages, language_counts = process_language_data(df)
    # movie_types, type_counts = process_movie_types(df)

    # context = {
    #     'movie_data': json.dumps(movie_data),
    #     'languages': json.dumps(languages),
    #     'language_counts': json.dumps(language_counts),
    #     'movie_types': json.dumps(movie_types),
    #     'type_counts': json.dumps(type_counts),
    # }

    # return render(request, 'analysis/movie_runtime.html', context)
