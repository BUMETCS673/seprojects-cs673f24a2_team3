from django.test import TestCase

# Create your tests here.


from django.contrib.auth.models import User

class UserSignUpTest(TestCase):
    def test_user_registration(self):
        user_data = {
            'username': 'testuser',
            'password': 'securepassword123',
            'email': 'testuser@example.com',
        }
        response = self.client.post('/signup/', user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/home/')
        user = User.objects.filter(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'testuser@example.com')

    def test_duplicate_username(self):
        User.objects.create_user(username='existinguser', password='password')
        response = self.client.post('/signup/', {
            'username': 'existinguser',
            'password': 'securepassword123',
            'email': 'duplicateuser@example.com',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Username already exists.")
