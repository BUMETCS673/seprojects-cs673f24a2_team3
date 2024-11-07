# 文件路径: analysis/tests.py

from django.test import TestCase
from django.urls import reverse

class HomePageViewTest(TestCase):
    def test_home_page_status_code(self):
        """
        测试主页是否能够成功加载（HTTP 200 状态码）
        """
        url = reverse('home')  # 假设主页的 URL 名称是 'home'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
