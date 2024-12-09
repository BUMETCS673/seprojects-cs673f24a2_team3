from django.test import TestCase
from django.urls import reverse

class ChartViewTest(TestCase):
    def test_runtime_chart_view(self):
        response = self.client.get(reverse('movie_runtime'))  
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analysis/movie_runtime.html')  # Ensure the correct template is used
        self.assertIn('runtime_data', response.context)  # Check if context contains 'chart_data'
