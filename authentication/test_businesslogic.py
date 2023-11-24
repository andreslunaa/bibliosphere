from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from authentication.models import Book, UserProfile, Genre
from authentication.business_logic import recommend, WebCrawl_Search
from authentication.tokens import generater_token
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import  force_bytes

class RecommendationTests(TestCase):
    def setUp(self):
        self.client = Client()


        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.genre = Genre.objects.create(name='Fantasy')
        self.token = generater_token.make_token(self.user)


        self.book1 = Book.objects.create(title='Book 1', author='Author 1', description='Description 1')
        self.book2 = Book.objects.create(title='Book 2', author='Author 2', description='Description 2')
        self.user_profile.preferred_genres.add(self.genre)
        self.book1.genres.add(self.genre)
        self.book2.genres.add(self.genre)


    def test_activate(self):

        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))

        response = self.client.get(reverse('activate', args=[uidb64, self.token]))

        self.assertTemplateUsed(response, 'authentication/signin.html')

        self.user.refresh_from_db()

        self.assertTrue(self.user.is_active)

    def test_recommend(self):

        recommendations = recommend(self.book1)
        recomlist = recommend(self.book2)


        self.assertIsInstance(recommendations, list)
        self.assertEqual(recomlist, [2])



    def test_webcrawl_search(self):
   
        web_crawler = WebCrawl_Search()

  
        search_results = web_crawler.search('Harry Potter')

        self.assertIsInstance(search_results, list)
        self.assertNotEqual(search_results,[])

