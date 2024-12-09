# code/my_project/tests.py

from django.test import TestCase

class BasicTest(TestCase):
    def test_basic(self):
        """A basic test that always passes."""
        self.assertEqual(1, 1)
