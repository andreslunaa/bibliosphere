from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from authentication.tokens import TokenGenerator, generater_token  

class TokenGeneratorTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com',
        )

    def test_generator_token(self):

        generator = TokenGenerator()

  
        token = generator._make_hash_value(self.user, 123456789)

        self.assertIsInstance(token, str)
        self.assertEqual(token,'1123456789')

