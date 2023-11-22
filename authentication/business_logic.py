from .models import Book, UserProfile
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import  force_str
from django.contrib.auth.models import User

from django.contrib.auth import login 
from . tokens import generater_token
from django.shortcuts import render

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Book
import time
import requests
from bs4 import BeautifulSoup

################################################################################


def find_books(request):
    books_by_genre = {}
    # Get preferred_genres from UserProfile
    user_profile = UserProfile.objects.get(user=request.user)
    selected_genres = list(user_profile.preferred_genres.values_list('name', flat=True))

    for genre in selected_genres:
        genre_books = Book.objects.filter(genres__name__icontains=genre).order_by('?')[:7]
        if genre_books.count() < 7:
            additional_books_needed = 7 - genre_books.count()
            other_books = Book.objects.exclude(id__in=[book.id for book in genre_books]).order_by('?')[:additional_books_needed]
            genre_books = list(genre_books) + list(other_books)
        books_by_genre[genre] = genre_books
    return books_by_genre

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)  # Fetch the User first
        user_profile = user.userprofile  # Assuming the reverse relation from User to UserProfile is 'userprofile'
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user_profile = None

    if user_profile is not None and generater_token.check_token(user_profile.user, token):
        user = user_profile.user
        user.is_active = True
        user.save()
        return render(request,'authentication/signin.html')
    else:
        return render(request,'activation_failed.html')
    
    
def saved_information(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    preferred_genres = user_profile.preferred_genres.all().order_by('name')
    return render(request, 'authentication/saved_information.html', {
        'user': request.user,
        'preferred_genres': preferred_genres
    })

def recommend(book):
    # Extract book ID from the Book object
    start_time = time.time()
    bookmarked_book_id = book.id

    queryset = get_books_around_id(bookmarked_book_id)

    #queryset = Book.objects.prefetch_related('genres').all().values('id', 'title', 'author', 'genres')
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
        print(f"Execution time total: {execution_time} seconds")
        return []


def get_books_around_id(target_id, radius=2000, max_books=4000):
    # Get the lowest and highest book ID in the dataset
    start_time = time.time()
    lowest_id = Book.objects.order_by('id').first().id if Book.objects.exists() else 0
    highest_id = Book.objects.order_by('-id').first().id if Book.objects.exists() else 0

    # Calculate the range, ensuring it stays within the dataset bounds
    min_id = max(lowest_id, target_id - radius)
    max_id = min(highest_id, target_id + radius)

    # Adjust the range if near the dataset boundaries
    if target_id - min_id < radius:
        max_id = min(max_id + (radius - (target_id - min_id)), highest_id)

    if max_id - target_id < radius:
        min_id = max(min_id - (radius - (max_id - target_id)), lowest_id)

    books = Book.objects.filter(id__gte=min_id, id__lte=max_id)[:max_books]

    end_time = time.time()  # End time measurement
    execution_time = end_time - start_time  # Calculate total execution time
    print(f"Execution time func 1: {execution_time} seconds")
    return books

class WebCrawl_Search:
    def __init__(self):
        self.base_url = "https://www.goodreads.com"
        self.headers = {"User-Agent": "Chrome/58.0.3029.110"}

    def search(self, query):
        url = f"https://www.goodreads.com/search?q={query.replace(' ', '+')}"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for link in soup.find_all('a', class_='bookTitle', href=True):
            links.append(link['href'])
        return links