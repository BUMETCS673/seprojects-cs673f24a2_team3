from django.test import TestCase
from analysis.utils import calculate_average_rating

class UtilsTest(TestCase):
    def test_calculate_average_rating(self):
        ratings = [8.5, 9.0, 7.5]
        result = calculate_average_rating(ratings)
        self.assertEqual(result, 8.33)  # Rounded to 2 decimals
