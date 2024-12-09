from django.shortcuts import render

# Create your views here.
from django.contrib import admin
from django.urls import path,include
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.core import serializers # 将django查询转换为 json
import json
from django.db import connection
import pandas as pd  # 使用pandas处理数据库的数据
# 配置 pymysql 方便 pandas 调用
import pymysql
db = pymysql.connect(host='db',
                     port=3306,
                     user='selina',  # 数据库用户名字
                     password='snowBall',  # 数据库密码
                     db='movie_data',  # 数据库的名字
                     charset='utf8')

# 首页
# 电影基本信息可视化


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


def fetch_data_from_db():
    """Fetches all movie data from the database using Django's connection."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM data")
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return pd.DataFrame(rows, columns=columns)

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

def process_top_production_companies(df):
    """Process and return top 20 production companies with split and count."""
    if 'production_company' in df.columns:
        # Split production companies by a comma delimiter
        companies = df['production_company'].str.split(',').explode().str.strip()
        # Count each company and sort by the highest counts
        company_counts = companies.value_counts().head(10)
        
        # Prepare data for the chart
        data = [{"name": company, "value": count} for company, count in company_counts.items()]
        return data 
    else:
        return []


def dashboard_view(request):
    df = fetch_data_from_db()

    # Process various visual data
    movie_distribution_by_year_intervals = process_movie_distribution_by_year_intervals(df)
    languages, language_counts = process_language_data(df)
    genres, genre_counts = process_movie_genres(df)
    top_companies = process_top_production_companies(df)

    context = {
        'movie_distribution_by_year_intervals': json.dumps(movie_distribution_by_year_intervals),
        'languages': json.dumps(languages),
        'language_counts': json.dumps(language_counts),
        'movie_genres': json.dumps(genres),
        'genre_counts': json.dumps(genre_counts),
        'top_companies': json.dumps(top_companies),
    }

    return render(request, 'analysis/dashboard.html', context)




def movie_runtime_view(request):
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

    return render(request, 'analysis/movie_runtime.html', context)


















# def movie_runtime_view(request):
#     # Data for dataAnalysisInfos
#     df = pd.read_sql('select * from data', db)
#     # 1上映年份电影数量饼图
#     quj = list(range(1921, 2023, 5))
#     fenzu = pd.cut(df.year, quj, right=False)  # 分组区间
#     pinshu = fenzu.value_counts().sort_index()
#     # print(pinshu,pinshu.index.tolist())
#     # 使用的是直接统计各个年份的方法 但是用户需要的是按照五年的步长来进行统计
#     # df1 = df.value_counts('year').sort_index()
#     # # print(df1.index.tolist(),df1.values.tolist())

#     # 年份区间列表
#     year_list = ['[1921, 1926)','[1926, 1931)','[1931, 1936)','[1936, 1941)','[1941, 1946)',
#                  '[1946, 1951)','[1951, 1956)','[1956, 1961)','[1961, 1966)','[1966, 1971)',
#                  '[1971, 1976)','[1976, 1981)','[1981, 1986)','[1986, 1991)','[1991, 1996)',
#                  '[1996, 2001)','[2001, 2006)','[2006, 2011)','[2011, 2016)','[2016, 2021)'
#                  ]
#     # 将2个列表转换为字典形式 提供给前端 echart ，这里的规格是echart规定的
#     lists = [list(a) for a in zip(pinshu.values.tolist(),year_list)]
#     # print(lists)
#     keys = ['value', 'name']
#     list_joson1 = [dict(zip(keys, item)) for item in lists]
#     # print(list_joson1)

#     # 2 语言和上映电影数量柱状图
#     language_list = [] # 语言出现的列表
#     # 提取语言的数据 按照空格进行分割 因为一部电影有的时候不止一种语言
#     for i in df['language']:
#         language_list=language_list +i.split(' ')
#     # print(language_list)
#     # 统计列表中各种语言出现的频率
#     dict2 = {}
#     for key in language_list:
#         dict2[key] = dict2.get(key, 0) + 1
#     # 删除空
#     del dict2['']
#     # 排序 reverse= True 降序排列
#     dict2 = dict(sorted(dict2.items(), key=lambda e: e[1], reverse=True))
#     # 将排序后的字典的键值对转换为列表
#     x2 = list(dict2)[:20]
#     y2 = list(dict2.values())[:20]
#     print(x2,y2)
#     # 3 电影类型和电影数量 折线图
#     # 统计类型的频数
#     df3 = df.value_counts('type')
#     type_list = []  # 语言出现的列表
#     # 提取语言的数据 按照空格进行分割 因为一部电影有的时候不止一种语言
#     for i in df['type']:
#         type_list = type_list + i.replace('\r\n','').split(',')
#     # print(language_list)
#     # 统计列表中各种语言出现的频率
#     dict2 = {}
#     for key in type_list:
#         key = key.replace(' ','')
#         dict2[key] = dict2.get(key, 0) + 1
#     # 排序 reverse= True 降序排列
#     dict2 = dict(sorted(dict2.items(), key=lambda e: e[1], reverse=True))
#     # 将排序后的字典的键值对转换为列表
#     x3 = list(dict2)
#     y3 = list(dict2.values())
#     print(x3,y3)
#     # 4 电影时长
#     df4 = df.copy()
#     # 转换电影时长为分钟
#     def dealtime(x):
#         # 有一些有？进行替换
#         x = x.replace('?','')
#         # print(x)
#         try:
#             h = int(x.split('h')[0])*60
#         except:
#             h=0
#         # 获取分钟
#         try:
#             m = int(x.split('h')[1].split('m')[0])
#         except:
#             m = 0
#         # 总分钟
#         runtime = h+m
#         # print(runtime)
#         return runtime
#     # 将时长转换为分钟为单位
#     df4['Runtime'] = df4['ontime'].apply(dealtime)
#     # print(df4.sort_values('Runtime')['Runtime'].tolist())
#     # 按照10分钟为步长进行分区
#     quj = list(range(67, 248, 10))
#     # 分组区间
#     fenzu = pd.cut(df4.Runtime, quj, right=False)  # 分组区间
#     # 统计各个区间的频数
#     pinshu = fenzu.value_counts().sort_index()

#     x4 = ['[67, 77)','[77, 87)','[87, 97)','[97, 107)','[107, 117)','[117, 127)','[127, 137)','[137, 147)','[147, 157)','[157, 167)','[167, 177)','[177, 187)','[187, 197)','[197, 207)','[207, 217)','[217, 227)','[227, 237)','[237, 247)']
#     y4 = pinshu.values.tolist()
#     # print(x4,y4)
#     # 5 国家或地区
#     country_list = []  # 国家出现的列表
#     # 提取国家的数据 按照,进行分割 因为一部电影有的时候不止一种国家
#     for i in df['production_country']:
#         country_list = country_list + i.split(',')
#     # print(language_list)
#     # 统计列表中各种国家出现的频率
#     dict3 = {}
#     for key in country_list:
#         dict3[key] = dict3.get(key, 0) + 1
#     # 排序 reverse= True 降序排列
#     dict3 = dict(sorted(dict3.items(), key=lambda e: e[1], reverse=True))
#     # 将排序后的字典的键值对转换为列表
#     x5 = list(dict3)[:20]
#     y5 = list(dict3.values())[:20]
#     # print(x5,y5)
#     lists = [list(a) for a in zip(y5,x5)]
#     # print(lists)
#     keys = ['value', 'name']
#     list_joson2 = [dict(zip(keys, item)) for item in lists]
#     # print(list_joson2)

   
#     # Combine all the data into a single context dictionary
#     context = {
#         'list_joson1': json.dumps(list_joson1),  # Serialize as JSON
#         'x2': json.dumps(x2),  # Serialize as JSON
#         'y2': json.dumps(y2),  # Serialize as JSON
#         'x3': json.dumps(x3),  # Serialize as JSON
#         'y3': json.dumps(y3),  # Serialize as JSON
#         'list_joson2': json.dumps(list_joson2),  # Serialize as JSON
#         'x5': json.dumps(x5),  # Serialize as JSON
#         'x4': json.dumps(x4),  # Serialize as JSON
#         'y4': json.dumps(y4),  # Serialize as JSON
#         # Add other data as needed
#     }

#     return render(request, 'analysis/movie_runtime.html', context)


# def top_production_companies_view(request):
#     # Query the data from the database
#     df = pd.read_sql('SELECT production_company FROM data', db)

#     # Split production_company entries (as movies may have multiple companies, separated by commas)
#     df['production_company'] = df['production_company'].str.split(',')

#     # Explode the DataFrame so each company gets its own row
#     df_exploded = df.explode('production_company')

#     # Count occurrences of each production company
#     company_counts = df_exploded['production_company'].value_counts().nlargest(20)

#     # Get the top 20 company names and their counts
#     company_names = company_counts.index.tolist()
#     company_values = company_counts.values.tolist()

#     # Pass the data to the template
#     context = {
#         'company_names': company_names,
#         'company_values': company_values,
#     }
#     return render(request, 'dashboard/top_companies_chart.html', context)


# 数据展示页面
#def data_view(request):
#    df = pd.read_sql('select * from data', db)
#    res = []
#    for i in range(len(df)):
#        # print(df.iloc[i].tolist())
#        res.append(df.iloc[i].tolist())
#   return render(request, 'data.html',locals() )



# def data_analysis_score(request):
#     # Read data from SQL database
#     df = pd.read_sql('SELECT * FROM data', db)

#     # 1. Count the number of movies in each score category
#     df_scores_count = df['score'].value_counts().sort_index()
#     score_labels = df_scores_count.index.tolist()
#     score_values = df_scores_count.values.tolist()

#     score_data = [{'value': value, 'name': score} for score, value in zip(score_labels, score_values)]

#     # 2. Radar chart: Average gross by score
#     df['Gross'] = df['Gross'].str.replace(',', '').astype(float)  # Clean and convert Gross to float
#     avg_gross_by_score = df.groupby('score')['Gross'].mean()
#     score_gross_labels = avg_gross_by_score.index.tolist()
#     avg_gross_values = avg_gross_by_score.tolist()

#     # Setting a max gross value for radar chart
#     max_gross_values = [550000000] * len(score_gross_labels)  # Static value based on example
#     radar_data = [{'name': score, 'max': max_gross} for score, max_gross in zip(score_gross_labels, max_gross_values)]

#     # 3. Relationship between companies and scores
#     df_company_score = df[['production_company', 'score']].copy()

#     # Expand the companies column into multiple rows for each movie
#     df_company_expanded = df_company_score.assign(
#         production_company=df_company_score['production_company'].str.split(',')
#     ).explode('production_company')

#     # Count occurrences of companies and sort by frequency
#     top_companies = df_company_expanded['production_company'].value_counts().nlargest(20)
#     top_company_names = top_companies.index.tolist()
#     top_company_counts = top_companies.values.tolist()

#     # 4. Scatter plot: Awards won by score
#     df_awards_by_score = df.groupby('score')['geted'].mean()
#     award_score_labels = df_awards_by_score.index.tolist()
#     avg_awards_values = df_awards_by_score.round(2).tolist()

#     award_data = [[score, avg_awards] for score, avg_awards in zip(award_score_labels, avg_awards_values)]

#     # Combine all the data into a single context dictionary and serialize as JSON
#     context = {
#         'list_joson1': json.dumps(score_data),  # Serialize score data
#         'x2': json.dumps(score_gross_labels),  # Serialize score labels for radar chart
#         'y2': json.dumps(avg_gross_values),  # Serialize average gross values for radar chart
#         'x3': json.dumps(top_company_names),  # Serialize company names
#         'y3': json.dumps(top_company_counts),  # Serialize company counts
#         'list_joson2': json.dumps(radar_data),  # Serialize radar chart data
#         'x4': json.dumps(award_score_labels),  # Serialize score labels for awards scatter plot
#         'y4': json.dumps(avg_awards_values),  # Serialize awards data
#         'list_joson4': json.dumps(award_data),  # Serialize awards scatter plot data
#         # Add any other data as needed
#     }

#     # Render the context to the HTML template
#     return render(request, 'analysis/index.html', context)



