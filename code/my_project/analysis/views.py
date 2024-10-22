from django.shortcuts import render

# Create your views here.
from django.contrib import admin
from django.urls import path,include
from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.core import serializers # 将django查询转换为 json
import json
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
    # Data for dataAnalysisInfos
    df = pd.read_sql('select * from data', db)
    # 1上映年份电影数量饼图
    quj = list(range(1921, 2023, 5))
    fenzu = pd.cut(df.year, quj, right=False)  # 分组区间
    pinshu = fenzu.value_counts().sort_index()
    # print(pinshu,pinshu.index.tolist())
    # 使用的是直接统计各个年份的方法 但是用户需要的是按照五年的步长来进行统计
    # df1 = df.value_counts('year').sort_index()
    # # print(df1.index.tolist(),df1.values.tolist())

    # 年份区间列表
    year_list = ['[1921, 1926)','[1926, 1931)','[1931, 1936)','[1936, 1941)','[1941, 1946)',
                 '[1946, 1951)','[1951, 1956)','[1956, 1961)','[1961, 1966)','[1966, 1971)',
                 '[1971, 1976)','[1976, 1981)','[1981, 1986)','[1986, 1991)','[1991, 1996)',
                 '[1996, 2001)','[2001, 2006)','[2006, 2011)','[2011, 2016)','[2016, 2021)'
                 ]
    # 将2个列表转换为字典形式 提供给前端 echart ，这里的规格是echart规定的
    lists = [list(a) for a in zip(pinshu.values.tolist(),year_list)]
    # print(lists)
    keys = ['value', 'name']
    list_joson1 = [dict(zip(keys, item)) for item in lists]
    # print(list_joson1)

    # 2 语言和上映电影数量柱状图
    language_list = [] # 语言出现的列表
    # 提取语言的数据 按照空格进行分割 因为一部电影有的时候不止一种语言
    for i in df['language']:
        language_list=language_list +i.split(' ')
    # print(language_list)
    # 统计列表中各种语言出现的频率
    dict2 = {}
    for key in language_list:
        dict2[key] = dict2.get(key, 0) + 1
    # 删除空
    del dict2['']
    # 排序 reverse= True 降序排列
    dict2 = dict(sorted(dict2.items(), key=lambda e: e[1], reverse=True))
    # 将排序后的字典的键值对转换为列表
    x2 = list(dict2)[:20]
    y2 = list(dict2.values())[:20]
    print(x2,y2)
    # 3 电影类型和电影数量 折线图
    # 统计类型的频数
    df3 = df.value_counts('type')
    type_list = []  # 语言出现的列表
    # 提取语言的数据 按照空格进行分割 因为一部电影有的时候不止一种语言
    for i in df['type']:
        type_list = type_list + i.replace('\r\n','').split(',')
    # print(language_list)
    # 统计列表中各种语言出现的频率
    dict2 = {}
    for key in type_list:
        key = key.replace(' ','')
        dict2[key] = dict2.get(key, 0) + 1
    # 排序 reverse= True 降序排列
    dict2 = dict(sorted(dict2.items(), key=lambda e: e[1], reverse=True))
    # 将排序后的字典的键值对转换为列表
    x3 = list(dict2)
    y3 = list(dict2.values())
    print(x3,y3)
    # 4 电影时长
    df4 = df.copy()
    # 转换电影时长为分钟
    def dealtime(x):
        # 有一些有？进行替换
        x = x.replace('?','')
        # print(x)
        try:
            h = int(x.split('h')[0])*60
        except:
            h=0
        # 获取分钟
        try:
            m = int(x.split('h')[1].split('m')[0])
        except:
            m = 0
        # 总分钟
        runtime = h+m
        # print(runtime)
        return runtime
    # 将时长转换为分钟为单位
    df4['Runtime'] = df4['ontime'].apply(dealtime)
    # print(df4.sort_values('Runtime')['Runtime'].tolist())
    # 按照10分钟为步长进行分区
    quj = list(range(67, 248, 10))
    # 分组区间
    fenzu = pd.cut(df4.Runtime, quj, right=False)  # 分组区间
    # 统计各个区间的频数
    pinshu = fenzu.value_counts().sort_index()

    x4 = ['[67, 77)','[77, 87)','[87, 97)','[97, 107)','[107, 117)','[117, 127)','[127, 137)','[137, 147)','[147, 157)','[157, 167)','[167, 177)','[177, 187)','[187, 197)','[197, 207)','[207, 217)','[217, 227)','[227, 237)','[237, 247)']
    y4 = pinshu.values.tolist()
    # print(x4,y4)
    # 5 国家或地区
    country_list = []  # 国家出现的列表
    # 提取国家的数据 按照,进行分割 因为一部电影有的时候不止一种国家
    for i in df['production_country']:
        country_list = country_list + i.split(',')
    # print(language_list)
    # 统计列表中各种国家出现的频率
    dict3 = {}
    for key in country_list:
        dict3[key] = dict3.get(key, 0) + 1
    # 排序 reverse= True 降序排列
    dict3 = dict(sorted(dict3.items(), key=lambda e: e[1], reverse=True))
    # 将排序后的字典的键值对转换为列表
    x5 = list(dict3)[:20]
    y5 = list(dict3.values())[:20]
    # print(x5,y5)
    lists = [list(a) for a in zip(y5,x5)]
    # print(lists)
    keys = ['value', 'name']
    list_joson2 = [dict(zip(keys, item)) for item in lists]
    # print(list_joson2)

   
    # Combine all the data into a single context dictionary
    context = {
        'list_joson1': json.dumps(list_joson1),  # Serialize as JSON
        'x2': json.dumps(x2),  # Serialize as JSON
        'y2': json.dumps(y2),  # Serialize as JSON
        'x3': json.dumps(x3),  # Serialize as JSON
        'y3': json.dumps(y3),  # Serialize as JSON
        'list_joson2': json.dumps(list_joson2),  # Serialize as JSON
        'x5': json.dumps(x5),  # Serialize as JSON
        'x4': json.dumps(x4),  # Serialize as JSON
        'y4': json.dumps(y4),  # Serialize as JSON
        # Add other data as needed
    }

    return render(request, 'analysis/index.html', context)



# 数据展示页面
#def data_view(request):
#    df = pd.read_sql('select * from data', db)
#    res = []
#    for i in range(len(df)):
#        # print(df.iloc[i].tolist())
#        res.append(df.iloc[i].tolist())
#   return render(request, 'data.html',locals() )



