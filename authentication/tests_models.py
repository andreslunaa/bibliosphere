from django.test import TestCase
from django.contrib.auth.models import User
from authentication.models import Genre, UserProfile, Book, Bookmark, Comment, Rating


class ModelTests(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='testpass')

        # Create a genre for testing
        self.genre = Genre.objects.create(name='Fiction')

        # Create a book for testing
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            rating=4.5,
            description='This is a test book.',
            isbn='1234567890',
            characters='Character 1, Character 2',
            pages='200',
            publisher='Test Publisher',
            awards='Best Test Book Award',
            liked_percent='90%',
            setting='Test Setting',
            coverImg='test_cover.jpg',
        )
        self.book.genres.add(self.genre)

        # Create a bookmark for testing
        self.bookmark = Bookmark.objects.create(user=self.user, book=self.book)

        # Create a comment for testing
        self.comment = Comment.objects.create(user=self.user, book=self.book, content='Great book!')

        # Create a rating for testing
        self.rating = Rating.objects.create(user=self.user, book=self.book, rating=5.0)

    def test_genre_str(self):
        self.assertEqual(str(self.genre), 'Fiction')
        self.assertNotEqual(str(self.genre), 'Mystery')

    def test_user_profile_str(self):
        user_profile = UserProfile.objects.create(user=self.user)
        user_profile.preferred_genres.add(self.genre)
        self.assertEqual(str(user_profile), 'testuser')
        self.assertNotEqual(str(user_profile), 'invaliduser')

    def test_book_str(self):
        self.assertEqual(str(self.book), 'Test Book by Test Author')
        self.assertNotEqual(str(self.book), 'Test Book by Other Author')

    def test_bookmark_str(self):
        self.assertEqual(str(self.bookmark), 'testuser - Test Book')
        self.assertNotEqual(str(self.bookmark), 'testuser - NIL Book')

    def test_comment_str(self):
        self.assertEqual(str(self.comment), 'Comment by testuser on Test Book')
        self.assertNotEqual(str(self.comment), 'NIL Comment by testuser on Test Book')

    def test_rating_str(self):
        self.assertEqual(str(self.rating), 'testuser rated Test Book as 5.0')
        self.assertNotEqual(str(self.rating), 'testuser rated Test Book as 3.0')
