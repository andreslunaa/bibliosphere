import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Book
import time

def recommend(book):
    # Extract book ID from the Book object
    start_time = time.time()
    bookmarked_book_id = book.id

    # Fetch books and prefetch related genres
    queryset = Book.objects.prefetch_related('genres').all()[:10000]

    # Prepare DataFrame including book IDs
    book_data = [{
        'id': book.id, 
        'title': book.title, 
        'author': book.author, 
        'genres': ' '.join(genre.name for genre in book.genres.all())
    } for book in queryset]
    df = pd.DataFrame(book_data)

    # Combine features
    df["combined_features"] = df.apply(lambda row: row['title'] + " " + row['author'] + " " + row['genres'], axis=1)

    # Vectorize combined features
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df["combined_features"])

    # Calculate cosine similarity
    cosine_sim = cosine_similarity(count_matrix)

    # Check if the DataFrame contains the bookmarked book ID and retrieve recommendations
    if bookmarked_book_id in df['id'].values:
        indexnum = df[df['id'] == bookmarked_book_id].index[0]
        similar_books = list(enumerate(cosine_sim[indexnum]))
        sorted_similar_books = sorted(similar_books, key=lambda x: x[1], reverse=True)

        # Get up to 10 recommended book IDs
        recomlist = [df['id'][sorted_similar_books[i][0]] for i in range(1, min(11, len(sorted_similar_books)))]
        end_time = time.time()  # End time measurement
        execution_time = end_time - start_time  # Calculate total execution time
        print(f"Execution time: {execution_time} seconds")
        return recomlist
    else:
        print("Book with ID {} not found in the dataset.".format(bookmarked_book_id))
        end_time = time.time()  # End time measurement
        execution_time = end_time - start_time  # Calculate total execution time
        print(f"Execution time: {execution_time} seconds")
        return []

