from django.shortcuts import render
from django.http import HttpResponse
from .models import UserText
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
from io import BytesIO

# 下载NLTK的词典数据，仅需在首次运行时启用
nltk.download('vader_lexicon')

def generate_wordcloud(request):
    # 从数据库获取最新的文本
    latest_text_entry = UserText.objects.latest('created_at')
    text = latest_text_entry.content

    # 进行情感分析
    sia = SentimentIntensityAnalyzer()
    sentiment_score = sia.polarity_scores(text)

    # 生成词云
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # 将词云图像保存到内存
    buffer = BytesIO()
    wordcloud.to_image().save(buffer, format="PNG")
    buffer.seek(0)

    # 返回词云图像作为 HTTP 响应
    return HttpResponse(buffer, content_type="image/png")
