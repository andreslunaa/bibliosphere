import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bibliosphere.settings")  
django.setup()

from authentication.models import Book
from algoliasearch.search_client import SearchClient
from django.conf import settings

def index_books_to_algolia():
    client = SearchClient.create(settings.ALGOLIA['APPLICATION_ID'], settings.ALGOLIA['API_KEY'])
    index = client.init_index('bibliosphere')

    books = Book.objects.all().values('id', 'title', 'author', 'coverImg')
    algolia_books = [{'objectID': book['id'], **book} for book in books]
    index.save_objects(algolia_books)

if __name__ == "__main__":
    index_books_to_algolia()