from django.test import TestCase
from analysis.forms import RegistrationForm

class RegistrationFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'account_name': 'testuser',
            'user_id': '1234567890',
            'password': 'Test@1234'
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_user_id(self):
        form_data = {
            'account_name': 'testuser',
            'user_id': '123',  # Too short
            'password': 'Test@1234'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('user_id', form.errors)

    def test_invalid_password(self):
        form_data = {
            'account_name': 'testuser',
            'user_id': '1234567890',
            'password': 'password'  # Weak password
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
