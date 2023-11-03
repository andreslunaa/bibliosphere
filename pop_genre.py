import os
import django
import csv
# Set the environment variable to your settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliosphere.settings')

# Setup Django
django.setup()

from authentication.models import Genre  

from authentication.models import Genre 
with open('unique_strings.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        genre, created = Genre.objects.get_or_create(name=row['genre_name'])  # assuming 'genre_name' is the column name in your CSV
