import csv
import os
import django
# Set the environment variable to your settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliosphere.settings')

# Setup Django
django.setup()

from authentication.models import Book, Genre


with open('books.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            genres_from_csv = eval(row['genres'])  # assuming genres are stored as a list of strings

            book = Book(
                title=row['title'],
                series=row['series'],
                author=row['author'],
                rating=row['rating'],
                description=row['description'],
                isbn=row['isbn'],
                characters=row['characters'],
                pages=row['pages'],
                publisher=row['publisher'],
                awards=row['awards'],
                liked_percent=row['likedPercent'],
                setting=row['setting'],
                coverImg=row['coverImg']
            )
            book.save()

            for genre_name in genres_from_csv:
                genre = Genre.objects.get(name=genre_name)  # We've already ensured these exist in the previous script
                book.genres.add(genre)

        except Exception as e:
            print(f"Error processing row: {row}. Error: {e}")

