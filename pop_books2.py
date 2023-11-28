import os
import django
import csv

# Set the environment variable to your settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliosphere.settings')

# Setup Django
django.setup()

from authentication.models import Book, Genre

# Rest of your script
with open('books.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Handle genres
        genre_str = row['genres'].strip("[]")
        genres = [genre.strip().strip("'") for genre in genre_str.split(',')] if genre_str else []

        genre_instances = []
        for genre_name in genres:
            if genre_name:  # Check if genre name is not empty
                genre, created = Genre.objects.get_or_create(name=genre_name)
                genre_instances.append(genre)

        # Create Book instance
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

        # Add genres
        book.genres.add(*genre_instances)
