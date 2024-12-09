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
from collections import Counter
import os
from django.conf import settings
from .models import Review

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


def fetch_movie_data():
    movies = Movie.objects.all().values('index','title', 'year', 'score', 'awards', 'type','gross','production_company','production_country','url','ontime','language','oscar_number')
    return pd.DataFrame(list(movies))

df = fetch_movie_data() # make df as global 

######################### For Dashboard View ###################
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

# Add an API Endpoint for funnel_data test
def funnel_data_api(request):
    df = fetch_movie_data()  #  fetches our movie data DataFrame
    funnel_data = process_funnel_data(df)  # Process the data using funnel data function
    return JsonResponse(funnel_data, safe=False)  # Return as JSON array

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

######################### For box_performance View ######################

def process_box_office_data(df):
    """
    Process the data for the box office visualization with scaled gross values.
    """

    # Ensure the 'production_country' column exists and split by ',' or '\r\n'
    if 'production_country' in df.columns:
        df['production_country'] = df['production_country'].str.split(',').explode().reset_index(drop=True)
        df['production_country'] = df['production_country'].str.strip()  # Remove extra spaces

    # Convert gross values to float, handling invalid data
    def safe_convert_gross(value):
        try:
            return float(value.replace(',', '')) / 1_000_000  # Convert to millions of dollars
        except (ValueError, AttributeError):
            return 0.0

    if 'gross' in df.columns:
        df['gross'] = df['gross'].apply(safe_convert_gross)

    # Group by year and production country
    grouped = df.groupby(['year', 'production_country'])

    # Aggregate data
    aggregated = grouped.agg({
        'gross': 'sum',  # Sum of gross revenue
        'title': 'count'  # Number of movies
    }).reset_index()

    # Filter for top 10 countries using an external helper function
    top_countries = process_funnel_data(df)
    top_country_names = [country['name'] for country in top_countries]

    # Create the box office data with year intervals
    box_office_data = []
    for start_year in range(1921, 2021, 10):  # Adjust year intervals (e.g., 1921-1925)
        interval_data = []
        for country in top_country_names:
            country_data = aggregated[
                (aggregated['year'] >= start_year) &
                (aggregated['year'] < start_year + 10) &
                (aggregated['production_country'].str.contains(country, na=False))
            ]
            interval_data.append({
                'name': country,
                'value': [
                    round(country_data['gross'].sum(), 2) if not country_data.empty else 0.0,  # Total gross revenue (scaled)
                    int(country_data['title'].sum()) if not country_data.empty else 0,         # Number of movies
                    next((item['value'] for item in top_countries if item['name'] == country), 0),  # Total static count for Bubble size
                    country                                                                    # Country name
                ]
            })
        box_office_data.append({
            'interval': f"{start_year}-{start_year + 10}",
            'data': interval_data
        })

    return box_office_data


def box_office_view(request):
   
    # Fetch movie data
    df = fetch_movie_data()

    # Process combinedData for ECharts
    box_office_data = process_box_office_data(df)

    # Pass the processed data to the template
    context = {
        'box_office_data': json.dumps(box_office_data),  # Ensure it's JSON-encoded for JavaScript
    }
    
    return render(request, 'analysis/box_office.html', context)  
  

######################### For Language_Diversity View ###################

def clean_and_preprocess_languages(df):
    """Clean and preprocess the 'language' column in the DataFrame."""
    if 'language' not in df.columns:
        return df
    
    # Clean and normalize the language column
    df['language'] = (
        df['language']
        .str.replace(r'\r\n', '', regex=True)
        .str.strip()
        .str.split(' ')
    )
    df = df.explode('language')
    df['language'] = df['language'].str.strip()

     # Correct common typos or inconsistencies
    typo_corrections = {
        "Japenses": "Japanese",  # Fix the typo
        # Add other typos or inconsistencies here
    }
    df['language'] = df['language'].replace(typo_corrections)

    # Replace empty strings with "Unknown"
    df['language'] = df['language'].replace('', 'Unknown').fillna('Unknown')
      
    return df

def process_language_stacked_bar_data(df, top_n=10):
    """
    Process language and genre data for stacked bar chart.
    Ensure the total percentage for each language sums to 100%.
    """
    if 'type' in df.columns and 'language' in df.columns:
        # Ensure unique index
        if not df.index.is_unique:
            df = df.reset_index(drop=True)

        # Add index column explicitly if not present
        if 'index' not in df.columns:
            df = df.reset_index()

        # Process the 'type' (genre) column
        df['type_split'] = df['type'].str.split(',')
        df = df.explode('type_split')
        df['type_split'] = df['type_split'].str.strip().fillna('Others')

        # Group smaller genres into 'Others'
        top_genres = df['type_split'].value_counts().nlargest(5).index
        df['type_split'] = df['type_split'].apply(lambda x: x if x in top_genres else 'Others') 

        # Process the 'language' column
        df['language_split'] = df['language'].str.split(' ')
        df = df.explode('language_split')
        df['language_split'] = df['language_split'].str.strip().replace('', 'Unknown').fillna('Unknown')

        # Group smaller languages into 'Others'
        top_languages = df['language_split'].value_counts().nlargest(top_n).index
        df['language_split'] = df['language_split'].apply(lambda x: x if x in top_languages else 'Others')

        # Exclude "Unknown" languages
        df = df[df['language_split'] != 'Unknown']

        # Normalize contributions per movie
        df['language_count'] = df.groupby('index')['language_split'].transform('count')
        df['genre_count'] = df.groupby('index')['type_split'].transform('count')
        df['weight'] = 1 / (df['language_count'] * df['genre_count'])

        # Group by language and genre, summing weights
        grouped = df.groupby(['language_split', 'type_split'])['weight'].sum().unstack(fill_value=0)

        # Normalize rows to ensure percentages sum to 100%
        def scale_to_100(row):
            total = row.sum()
            if total == 0:
                return row  # Skip empty rows
            # Scale all categories proportionally
            return row / total

        grouped = grouped.apply(scale_to_100, axis=1)

        # Prepare chart data
        chart_data = {
            "languages": grouped.index.tolist(),
            "genres": grouped.columns.tolist(),
            "data": grouped.values.tolist(),
        }

        return chart_data

    return {"languages": [], "genres": [], "data": []}



def process_language_map_data(df):
    """
    Process language map data and add coordinates.
    """
    COUNTRY_COORDINATES = {
        "United States": [-100, 40],
        "United Kingdom": [-1.5, 54],
        "France": [2.2137, 46.2276],
        "Germany": [10.4515, 51.1657],
        "Australia": [133.7751, -25.2744],
        "India": [78.9629, 20.5937],
        "Japan": [138.2529, 36.2048],
        "Italy": [12.5674, 41.8719],
        "Spain": [-3.7038, 40.4168],
        "Sweden": [18.6435, 60.1282],
    }
    # Clean and preprocess languages
    df = clean_and_preprocess_languages(df)

    # Extract production country and languages
    df['production_country'] = df['production_country'].str.split(',')
    country_data = df.explode('production_country')
    country_data['production_country'] = country_data['production_country'].str.strip()

    # Top 10 countries
    top_countries = (
        country_data['production_country'].value_counts().head(10).index
    )
    country_data = country_data[country_data['production_country'].isin(top_countries)]

    # Aggregate language data per country
    map_data = []
    for country, group in country_data.groupby('production_country'):
        total_movies = len(group)
        language_counts = group['language'].value_counts()

        # Handle "Multilingual" group
        top_languages = language_counts.head(3)
        multilingual_count = total_movies - top_languages.sum()
        if multilingual_count > 0:
            top_languages['Multilingual'] = multilingual_count

        # Prepare language data for the country
        language_data = [
            {"name": lang, "value": int(count)}
            for lang, count in top_languages.items()
        ]
        map_data.append({
            "name": country,
            "value": total_movies,
            "languages": language_data,
            "coordinates": COUNTRY_COORDINATES.get(country, [0, 0])  # Default to [0, 0] if not found
        })

    return map_data

def language_map_view(request):
    """Django view to return map data."""
    df = fetch_movie_data()
    map_data = process_language_map_data(df)
    return JsonResponse(map_data, safe=False)


def language_diversity_view(request):
    """View for Language Diversity Analysis."""
    # Fetch data from the Movie model
    df = fetch_movie_data()  
    # Prepare data for the visualizations
    stacked_bar_chart_data = process_language_stacked_bar_data(df)
    # tree_chart_data = process_language_treechart_data(df)
    map_data = process_language_map_data(df)
    context = {
        'stacked_bar_chart_data': json.dumps(stacked_bar_chart_data),
        'map_data': json.dumps(map_data),
    }
    
    return render(request, 'analysis/language_diversity.html', context)


######################### For genre_insights View ###################

def process_genre_timeline(df):
    """
    Processes movie genre data for timeline and pie chart.
    Groups genres contributing less than 5% into 'Others'.
    """
    if 'year' in df.columns and 'type' in df.columns:
        # Clean the 'type' column to remove unwanted characters
        df['type'] = df['type'].str.replace(r'[\r\n]', '', regex=True).str.strip()

        # Define year intervals (e.g., 1921-1931, 1931-1941, ..., 2011-2021)
        bins = list(range(1921, 2022, 10))
        labels = [f"{start}-{start + 10}" for start in bins[:-1]]
        df['year_interval'] = pd.cut(df['year'], bins=bins, labels=labels, right=False)

        # Split genres and count occurrences per interval
        genre_counts = df.assign(type=df['type'].str.split(',')).explode('type')
        grouped = genre_counts.groupby(['year_interval', 'type']).size().unstack(fill_value=0)

        # Calculate total counts per genre across all intervals
        total_counts = grouped.sum(axis=0)
        grand_total = total_counts.sum()
        percentages = total_counts / grand_total * 100

        # Identify main genres (>= 5%) and others (< 5%)
        main_genres = total_counts[percentages >= 5].index.tolist()
        grouped['Others'] = grouped[total_counts[percentages < 5].index].sum(axis=1)
        grouped = grouped[main_genres + ['Others']]

        # Reset index and prepare the dataset for ECharts
        grouped = grouped.reset_index()
        combined_data = [['Year'] + grouped.columns[1:].tolist()]  # Header row
        combined_data += grouped.values.tolist()  # Data rows
        return combined_data
    else:
        return [["Year"]]


def genre_insights_view(request):
    
    
    # Fetch movie data
    df = fetch_movie_data()

    # Process combinedData for ECharts
    combined_data = process_genre_timeline(df)

    # Pass the processed data to the template
    context = {
        'combinedData': json.dumps(combined_data),  # Ensure it's JSON-encoded for JavaScript
    }
    return render(request, 'analysis/genre_insights.html', context)





############ help fuction for oscar_number
# def ordinal(number):
#     """
#     Converts an integer into its ordinal representation (e.g., 1 -> 1st, 2 -> 2nd).
#     """
#     if not number:
#         return None
#     suffix = ['th', 'st', 'nd', 'rd', 'th'][min(number % 10, 4)]
#     if 11 <= (number % 100) <= 13:
#         suffix = 'th'
#     return f"{number}{suffix}"

# movie = Movie.objects.get(pk=1)
# print(f"{movie.title} won awards at the {ordinal(movie.oscar_number)} Oscars.")

######################## For movie_runtime View ###################

def clean_runtime_data(df):
    """
    Cleans the 'ontime' column by converting runtimes into numeric values (in minutes).
    """
    def convert_runtime_to_minutes(runtime):
        try:
            # Regex to match runtime patterns
            match = re.match(r"(\d+)h(?:\s*(\d+)m)?", runtime)
            if match:
                hours = int(match.group(1))  # Extract hours
                minutes = int(match.group(2)) if match.group(2) else 0  # Extract minutes
                return hours * 60 + minutes
            match = re.match(r"(\d+)m", runtime)  # Match cases with only 'm'
            if match:
                return int(match.group(1))
            return None  # Return None for invalid formats
        except:
            return None

    # Apply the conversion to the 'ontime' column
    df['ontime'] = df['ontime'].apply(convert_runtime_to_minutes)

    # Drop rows with invalid or missing runtimes
    df = df.dropna(subset=['ontime'])

    # Keep only positive runtimes
    return df[df['ontime'] > 0]

def process_runtime_data(df):
    """
    Groups movie runtimes into broader and detailed ranges and calculates their distribution.
    """
    # Define broader runtime ranges
    broad_bins = [0, 60, 90, 120, 150, 180, 210, 240, float('inf')]
    broad_labels = ['0-60', '60-90', '90-120', '120-150', '150-180', '180-210', '210-240', '240+']

    # Group movies into broad runtime ranges
    df['broad_runtime_range'] = pd.cut(df['ontime'], bins=broad_bins, labels=broad_labels, right=False)
    broad_data = df['broad_runtime_range'].value_counts().sort_index()

    # Define detailed runtime ranges for each broad range
    detailed_bins = {
        '0-60': [0, 30, 45, 60],
        '60-90': [60, 70, 80, 90],
        '90-120': [90, 100, 110, 120],
        '120-150': [120, 130, 140, 150],
        '150-180': [150, 160, 170, 180],
        '180-210': [180, 190, 200, 210],
        '210-240': [210, 220, 230, 240],
        '240+': [240, float('inf')],
    }

    detailed_data = {}
    for broad_label, bins in detailed_bins.items():
        # Filter data for the specific broad range
        range_df = df[df['broad_runtime_range'] == broad_label]
        if not range_df.empty:
            range_df['detailed_runtime_range'] = pd.cut(range_df['ontime'], bins=bins, right=False)
            detailed_counts = range_df['detailed_runtime_range'].value_counts().sort_index()
            # Convert Interval to string for JSON serialization
            detailed_data[broad_label] = {
                'ranges': [f"{interval.left}-{interval.right}" for interval in detailed_counts.index],
                'counts': detailed_counts.values.tolist()
            }

    # Prepare the final data
    return {
        'broad': {
            'ranges': broad_data.index.tolist(),
            'counts': broad_data.values.tolist()
        },
        'detailed': detailed_data
    }

    
def movie_runtime_view(request):
    # Fetch movie data
    df = fetch_movie_data()

    # Clean the data
    df = clean_runtime_data(df)

    # Process the data
    runtime_data = process_runtime_data(df)

    # Prepare data for the template
    context = {
        'runtime_data': json.dumps(runtime_data)  # Pass both broad and detailed data
    }

    return render(request, 'analysis/movie_runtime.html', context)

def fetch_reviews_data():
    reviews = Review.objects.all().values('content')
    return pd.DataFrame(list(reviews))

def clean_text(content_series, stopwords_path):
    """Clean and preprocess text data."""
    combined_text = ' '.join(content_series.fillna(''))
    combined_text = re.sub(r'[^\w\s]', '', combined_text).lower()
    stopwords_full_path = os.path.join(settings.BASE_DIR, stopwords_path)
    with open(stopwords_full_path, 'r', encoding='utf-8') as f:
        stopwords = set(f.read().splitlines())
    words = combined_text.split()
    filtered_words = [word for word in words if word not in stopwords]
    return filtered_words

def generate_word_frequency(words, top_n=50):
    """Generate word frequency data."""
    word_counts = Counter(words)
    return word_counts.most_common(top_n)

def word_cloud_view(request):
    """API endpoint to return word cloud data."""
    stopwords_path = 'analysis/stopword_en.txt'
    df_reviews = fetch_reviews_data()
    cleaned_words = clean_text(df_reviews['content'], stopwords_path)
    word_frequencies = generate_word_frequency(cleaned_words)
    echarts_data = [{"name": word, "value": count} for word, count in word_frequencies]
    return JsonResponse(echarts_data, safe=False)

def word_cloud_page(request):
    """Render word cloud page."""
    return render(request, 'analysis/wordCloud.html')