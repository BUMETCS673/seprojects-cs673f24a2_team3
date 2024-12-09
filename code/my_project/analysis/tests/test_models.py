from django.test import TestCase
from analysis.models import Movie

class MovieModelTest(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Inception",
            genre="Sci-Fi",
            rating=8.8,
            release_year=2010
        )

    def test_movie_creation(self):
        self.assertEqual(self.movie.title, "Inception")
        self.assertEqual(self.movie.genre, "Sci-Fi")
        self.assertEqual(self.movie.rating, 8.8)
        self.assertEqual(self.movie.release_year, 2010)

    def test_str_representation(self):
        self.assertEqual(str(self.movie), "Inception")
