from django.urls import path
from . import  views
app_name = 'analysis'
urlpatterns = [

    path('',views.index,name = 'index'),#首页
    path('data',views.data_view,name='data'),#数据列表
    path('dataAnalysisInfos',views.dataAnalysisInfos,name='dataAnalysisInfos'),#电影基本信息可视化函数
    path('dataAnalysisScore',views.dataAnalysisScore,name='dataAnalysisScore'),#电影评分可视化函数
    path('worldCloud',views.worldCloud,name='worldCloud'),#词云

]