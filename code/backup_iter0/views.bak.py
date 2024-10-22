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
def index(request):
    return render(request,'index.html')

# 数据展示页面
def data_view(request):
    df = pd.read_sql('select * from data', db)
    res = []
    for i in range(len(df)):
        # print(df.iloc[i].tolist())
        res.append(df.iloc[i].tolist())
    return render(request, 'data.html',locals() )



# 电影基本信息可视化
def dataAnalysisInfos(request):

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

    return render(request,'analysis.html',{'list_joson1':list_joson1,'x2':x2,'y2':y2,'x3':x3,'y3':y3,'list_joson2':list_joson2,'x5':x5,'x4':x4,'y4':y4})


# 电影评分相关数据可视化
def dataAnalysisScore(request):
    df = pd.read_sql('select * from data', db)
    # 1 各分段对应的电影数量
    df1 = df.copy()
    df1 = df1.value_counts('score')
    x1 = df1.index.tolist()
    y1 = df1.values.tolist()
    lists = [list(a) for a in zip(y1, x1)]

    keys = ['value', 'name']
    list_joson1 = [dict(zip(keys, item)) for item in lists]
    # print(x1)
    # print(list_joson1)

    # 2 评分和票房的雷达图
    df2 = df.copy()
    # 将票房数据转换为数值型
    def datatofloat(x):
        x = x.replace(',','')
        return float(x)
    df2['Gross'] = df2['Gross'].apply(datatofloat)
    # 按照评分来计算票房的平均值
    df2 = df2.groupby('score').mean()
    # print(df2)
    # 提取索引和票房平均数据
    x2 = df2.index.tolist()
    y2 = df2.Gross.tolist()
    # 设置一个规范 方便填充数据
    y2_index = [550000000,550000000,550000000,550000000,550000000,550000000,550000000,550000000,590000000,550000000,550000000,550000000,550000000]
    # print(x2,y2)
    lists = [list(a) for a in zip(x2,y2_index )]
    keys = ['name', 'max']
    list_joson2 = [dict(zip(keys, item)) for item in lists]
    print(y2)
    print(list_joson2)

    # 3 公司和评分之间的关系
    # 嵌套列表来添加 公司和评分 然后根据公司来做分组求均值 就得到了各个公司和评分之间的关系
    data3  = []
    df3 = df.copy()
    for i in range(len(df3)):
        # 提取公司
        compys = df3.iloc[i]['production_company'].split(',')
        # 提取评分
        rating = df3.iloc[i]['score']
        # 处理公司，一部电影一般都有多个公司拍摄 用,分割
        for j in compys:
            data3.append([j])
    df3_end = pd.DataFrame(data3,columns=['comp'])
    # print(df3_end)
    # 统计公司出现频率 并按照出现频率进行排序 取前20
    df3_end = df3_end.value_counts().sort_values(ascending=False)[:20]
    # 提取公司名字和排名进行
    x3 = df3_end.index.tolist()
    y3 = df3_end.values.tolist()
    # 处理 公司名字列表
    x3_2 = []
    for i in x3:
        # print(str(i).replace("(","").replace(")","").replace("'","").replace(',',''))
        x3_2.append(str(i).replace("(","").replace(")","").replace("'","").replace(',',''))
    # print(df3_end)
    # print(x3_2,y3)

    # 评分和获奖情况散点图
    df4 = df.copy()
    # 按照评分进行分组 然后求和
    df4 = df4.groupby('score').mean()
    # print(df4)
    x4 = df4.index.tolist()
    y4 = df4.geted.tolist()
    # 对小数进行处理
    y4_2 = []
    for i in y4:
        y4_2.append(round(i, 2))
    print(x4,y4_2)
    list_joson4 =[]
    for i in range(len(x4)):
        list_joson4.append([x4[i],round(y4[i], 2)])
    print(list_joson4)
    return render(request, 'analysisScore.html', {'x1':x1,'y1':y1,'list_joson1':list_joson1,'list_joson2':list_joson2,'y2':y2,'x3':x3_2,'y3':y3,'x4':x4,'y4':y4_2,'list_joson4':list_joson4})

# 统计词频
def word_count(str):
    counts = dict()
    words = str.split()

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    return counts

# 词云
def worldCloud(request):
    # 从数据库读取数据
    df = pd.read_sql('select * from reviews', db)
    # print(df[:5]['content'])
    # 提取评论的内容
    content2 = df['content']

    # 构建成一整个字符串内容
    strings2 = ''
    for i in content2:
        strings2 += str(i)
    strings2 = strings2.replace('I`m','')
    # 读取评论去掉一些无意义的数据
    import re
    pattern = re.compile('"\(\),.')

    strings2 = pattern.sub("", strings2)
    strings2 = strings2.replace('\\','')
    strings2 = strings2.replace(',', '')
    strings2 = strings2.replace('&', '')
    strings2 = strings2.replace('.', '')
    # print(strings2)
    # 进行词频统计
    words = word_count(strings2)
    # print(words)
    # # 读取停用词
    stop = open('dataAnalysis/stopword_en.txt', 'r+', encoding='utf-8')
    stopword = stop.read().split("\n")
    # 展示停用词
    # print(stopword)
    # 去掉停用词
    for word in list(words.keys()):
        if word in stopword:
            del words[word]
    word_counts = dict(sorted(words.items(), key=lambda e: e[1], reverse=True))

    #将词频字典转换为列表形式
    def dict_slice(adict, start, end):
        keys = adict.keys()
        list_slice = []
        for k in list(keys)[start:end]:
            dict_slice = (k, adict[k])
            list_slice.append(dict_slice)
        return list_slice

    # 提取词频字典的数据转换为嵌套列表方便下面进行使用
    word_counts = dict_slice(word_counts, 1, 300)
    print(word_counts)

    # 使用 pyechart 做图
    from pyecharts import options as opts
    from pyecharts.charts import WordCloud
    from pyecharts.globals import SymbolType

    worldcloud = (
        WordCloud()
            .add("", word_counts, word_size_range=[20, 50],
                 shape=SymbolType.DIAMOND ,# 背景图片,
                 )
            .set_global_opts(title_opts=opts.TitleOpts(title="WordCloud-IMDB"))
    )

    worldcloud.render('templates/worldCloud.html')

    # c.render_notebook()
    return render(request, 'worldCloud.html', {})

