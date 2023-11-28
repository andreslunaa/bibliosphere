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

    # Clear the index to remove all existing records
    index.clear_objects()

    # Retrieve all books from the database
    books = Book.objects.all().values('id', 'title', 'author', 'coverImg')

    # Prepare the data for Algolia
    algolia_books = [{'objectID': book['id'], **book} for book in books]

    # Save the new objects to the index
    index.save_objects(algolia_books)

if __name__ == "__main__":
    index_books_to_algolia()
