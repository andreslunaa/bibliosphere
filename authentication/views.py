from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage

from . tokens import generater_token
from bibliosphere import settings

from .models import Book, UserProfile, Genre, Bookmark, Comment, Rating
import random
from django.db import IntegrityError
from django.db.models import Avg

from django.http import HttpResponseRedirect
from django.shortcuts import render
import ast

from .business_logic import find_books, WebCrawl_Search, recommend 
from django.db.models import Q
from algoliasearch.search_client import SearchClient
from django.conf import settings
################################################################################################################################


def home(request):

    query = request.GET.get('search')
    books_by_genre = {}

    if query:
        # Initialize Algolia client and index
        client = SearchClient.create(settings.ALGOLIA['APPLICATION_ID'], settings.ALGOLIA['API_KEY'])
        index = client.init_index('bibliosphere')

        # Perform search on Algolia
        algolia_results = index.search(query)

        # Extract book information from results
        books = [hit for hit in algolia_results['hits']]
        
        return render(request, 'authentication/index.html', {'books': books})

    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        selected_genres = list(user_profile.preferred_genres.values_list('name', flat=True))
    else:
        selected_genres = random.sample(list(Genre.objects.values_list('name', flat=True)), 5)

    genre_books = Book.objects.filter(genres__name__in=selected_genres).order_by('?')
    for genre_name in selected_genres:
        books_by_genre[genre_name] = genre_books.filter(genres__name=genre_name)[:7]


    return render(request, 'authentication/index.html', {'books_by_genre': books_by_genre})

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password = request.POST.get('pass1')
        confirm_password = request.POST.get('pass2')


        # Check if the username exists in the User model
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username Already Exists!")
            return redirect('home')
        
        # Check if the email exists in the User model
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Exists!")
            return redirect('home')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric!")
            return redirect('home')

        try:
            # Create a user using the User model
            user = User.objects.create_user(username=username, email=email, password=password, first_name=fname, last_name=lname, is_active=False)
            user.save()


            # Create a UserProfile for the created User
            user_profile = UserProfile(user=user)
            user_profile.save()

            
            selected_genres = request.POST.getlist('genres[]')
            for genre_name in selected_genres:
                genre, created = Genre.objects.get_or_create(name=genre_name)
                user_profile.preferred_genres.add(genre)
            user_profile.save()

            messages.success(request, "Your Account Has Been Successfully created! Please check your email to activate your account.")
        except Exception as e:
            messages.error(request, str(e))
            return redirect('home')

        # Welcome Email
        '''
        subject = "Welcome to Bibliosphere"
        message = "Welcome to Bibliosphere, " + fname + " " + lname + "! \n\n Thank you for registering to our website. We have sent you a confimation email, please confirm your email to activate your account. \n\n Best regards, \n \n Bibliosphere Team"
        from_email = settings.EMAIL_HOST_USER
        to_list = [user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        '''
    
        #Email address confirmation
        current_site = get_current_site(request)
        email_subject = "Confirm Your Email Address"
        message2 = render_to_string('email_confirmation.html', {
            'name' : user.first_name,
            'domain' : current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generater_token.make_token(user),
            })
        email = EmailMessage(email_subject, message2, settings.EMAIL_HOST_USER, [user.email])
        email.fail_silently = True
        email.send()
        
        return redirect('signin')

    genres = [ 'Adventure', 'Children', 'Comedy', 'Fantasy', 'History', 'Mystery', 'Romance', 'Science Fiction','Thriller','Young Adult']
    return render(request, 'authentication/signup.html', {'genres': genres})

def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('pass1')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            books_by_genre = find_books(request)
            messages.success(request, "You have been successfully signed in!")
            return render(request, 'authentication/index.html', {'books_by_genre': books_by_genre})
        else:
            messages.error(request, "Invalid Credentials!")
            return redirect('home')

    return render(request, 'authentication/signin.html')

def signout(request):
    logout(request)
    messages.success(request, "You have been successfully signed out!")
    return redirect('home')

def preferred_genres(request):
    user = request.user
    context = {}

    try:
        user_profile = UserProfile.objects.get(user=user)
        preferred_genres_qs = user_profile.preferred_genres.all()
    except UserProfile.DoesNotExist:
        user_profile = None
        preferred_genres_qs = Genre.objects.none()

    if request.method == 'POST':
        if user_profile:
            # Get IDs of currently selected genres from the form, convert them to integers
            selected_genre_ids = set(int(genre_id) for genre_id in request.POST.getlist('preferred_genres'))
            
            # Get IDs of already preferred genres
            current_genre_ids = set(genre.id for genre in preferred_genres_qs)
            
            # Determine which genres need to be added or removed
            genres_to_add = selected_genre_ids - current_genre_ids
            genres_to_remove = current_genre_ids - selected_genre_ids

            # Add new genres
            for genre_id in genres_to_add:
                user_profile.preferred_genres.add(genre_id)

            # Remove deselected genres
            for genre_id in genres_to_remove:
                user_profile.preferred_genres.remove(genre_id)

            user_profile.save()
            return redirect('home')  
        else:
            context['error'] = "User profile does not exist."

    # Get the common genres
    common_genres_qs = Genre.objects.filter(name__in=[
        'Action', 'Adventure', 'Classics', 'Comic Book', 'Detective',
        'Mystery', 'Fantasy', 'Historical Fiction', 'Horror', 'Literary Fiction',
        'Romance', 'Science Fiction', 'Short Stories', 'Thrillers', 'Biographies'
    ])

    context['user_preferred_genre_ids'] = [genre.id for genre in preferred_genres_qs]
    context['common_genres'] = common_genres_qs
    return render(request, 'authentication/preferred_genres.html', context)

def search_and_select_genres(request):
    if request.method == 'POST':
        # Fetch the user profile
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Fetch the IDs of the genres that were checked in the form
        selected_genre_ids = request.POST.getlist('genre_ids')
        
        # Here we are adding genres to preferred genres, not setting or clearing them
        for genre_id in selected_genre_ids:
            genre, created = Genre.objects.get_or_create(id=genre_id)
            user_profile.preferred_genres.add(genre)
            
        # After updating, redirect to the preferred genres page
        messages.success(request, 'Your preferred genres have been updated.')
        return redirect('preferred_genres')

    # This handles the GET request to display genres based on the search term
    search_term = request.GET.get('search_term', '')
    matching_genres = Genre.objects.filter(name__icontains=search_term) if search_term else Genre.objects.none()
    
    return render(request, 'authentication/genre_search.html', {
        'matching_genres': matching_genres,
        'search_term': search_term
    })

def drop_preferred_genres(request):

    user = request.user
    context = {}

    try:
        user_profile = UserProfile.objects.get(user=user)
        preferred_genres_qs = user_profile.preferred_genres.order_by('name')
    except UserProfile.DoesNotExist:
        # Handle the case where the user does not have a profile
        return redirect('create_profile')

    if request.method == 'POST':
        # Get the list of genre ids that were checked
        checked_genre_ids = request.POST.getlist('preferred_genres')
        checked_genre_ids = set(map(int, checked_genre_ids))  # Convert to a set of integers

        # Update the user's preferred genres
        user_profile.preferred_genres.set(checked_genre_ids)
        user_profile.save()

        # Redirect to prevent double submission
        messages.success(request, 'Your preferred genres have been updated.')
        return redirect('home')

    # Create a list of tuples with genre name and id for the template
    preferred_genres_list = [(genre.id, genre.name) for genre in preferred_genres_qs]
    context['preferred_genres'] = preferred_genres_list

    return render(request, 'authentication/drop_preferred_genres.html', context)

def edit_user_info(request):

    if request.method == 'POST':
        user = request.user
        new_username = request.POST.get('username')
        new_first_name = request.POST.get('first_name')
        new_last_name = request.POST.get('last_name')

        # Check if the username has changed to a new one that doesn't exist yet
        if new_username and new_username != user.username:
            if User.objects.filter(username=new_username).exists():
                messages.error(request, 'Username already exists.')
                return render(request, 'authentication/edit_info.html')

        # Proceed to update the user
        try:
            if new_username:
                user.username = new_username
            if new_first_name:
                user.first_name = new_first_name
            if new_last_name:
                user.last_name = new_last_name

            user.save()
            messages.success(request, 'Your profile was successfully updated!')
        except IntegrityError as e:
            messages.error(request, 'There was an error updating your profile. Please try again.')

        return redirect('saved_information')

    return render(request, 'authentication/edit_info.html')

def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    is_bookmarked = False
    links = None

    # Web crawl functionality (should be accessible to all users)
    query = book.title
    webcrawl = WebCrawl_Search()
    webcrawl_links = webcrawl.search(query)
    if webcrawl_links:
        links = webcrawl.base_url + webcrawl_links[0]

   # Process awards, characters, setting (accessible to all users)
    for attr in ['awards', 'characters', 'setting']:
        attr_value = getattr(book, attr, '')
        if attr_value:
            if attr == 'awards':
                # Parse the awards list
                # Assuming the awards are stored as a string that looks like a list of strings
                try:
                    awards_list = ast.literal_eval(attr_value)
                except (ValueError, SyntaxError):
                    # Handle the case where the string cannot be parsed as a list
                    awards_list = []
                setattr(book, attr, awards_list)
            else:
                # General processing for characters and setting
                clean_str = attr_value.strip("[]").replace("'", "")
                setattr(book, attr, clean_str)
        else:
            setattr(book, attr, 'None')

    # Fetch comments (accessible to all users)
    comments = Comment.objects.filter(book=book).order_by('-created_at')
    average_rating = Rating.objects.filter(book=book).aggregate(Avg('rating'))['rating__avg']

    # Check bookmark status only if user is authenticated
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, book=book).exists()

    print(book.title)
    recommended_ids = recommend(book)
    recommended_books = Book.objects.filter(id__in=recommended_ids)

    context = {
        'book': book,
        'links': links,
        'comments': comments,
        'average_rating': average_rating,
        'is_bookmarked': is_bookmarked,
        'recommended_books': recommended_books
    }

    return render(request, 'authentication/book_detail.html', context)

def add_rating(request, book_id):
    if request.method == 'POST' and request.user.is_authenticated:
        book = get_object_or_404(Book, pk=book_id)
        rating_value = float(request.POST.get('rating'))
        Rating.objects.update_or_create(user=request.user, book=book, defaults={'rating': rating_value})
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('signin')

@login_required
def user_ratings(request):
    ratings = Rating.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'ratings': ratings
    }
    return render(request, 'authentication/user_ratings.html', context)

def add_bookmark(request, book_id):
    if request.user.is_authenticated:
        book = get_object_or_404(Book, pk=book_id)
        Bookmark.objects.get_or_create(user=request.user, book=book)
        return redirect('book_detail', book_id=book_id)  # Redirect to the book's detail page
    else:
        return redirect('signin')
    
def list_bookmarks(request):
    if request.user.is_authenticated:
        bookmarks = Bookmark.objects.filter(user=request.user).select_related('book')
        return render(request, 'authentication/bookmarks.html', {'bookmarks': bookmarks})
    else:
        return redirect('signin')
    
def remove_bookmark(request, book_id):
    if request.user.is_authenticated:
        book = get_object_or_404(Book, pk=book_id)
        Bookmark.objects.filter(user=request.user, book=book).delete()
        is_bookmarked = Bookmark.objects.filter(user=request.user, book=book).exists()

        # Existing web crawl functionality
        query = book.title
        webcrawl = WebCrawl_Search()
        webcrawl_links = webcrawl.search(query)
        links = webcrawl.base_url + webcrawl_links[0]
        
        # Pass 'book', 'links', and 'is_bookmarked' to the context
        context = {
            'book': book,
            'links': links,
            'is_bookmarked': is_bookmarked  # Include the is_bookmarked flag
        }

        next_page = request.GET.get('next') or 'book_detail'
        return redirect(next_page, book_id=book_id) if next_page == 'book_detail' else redirect(next_page)

        # Redirect back to the book's detail page
        #return redirect('authentication/book_detail', context)
    else:
        return redirect('signin')
    
def add_comment(request, book_id):
    if request.method == 'POST' and request.user.is_authenticated:
        book = get_object_or_404(Book, pk=book_id)
        content = request.POST.get('content')
        Comment.objects.create(user=request.user, book=book, content=content)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('signin')

@login_required
def user_comments(request):
    comments = Comment.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'comments': comments
    }
    return render(request, 'authentication/user_comments.html', context)

def recommendation_view(request, book_id):
    # Retrieve the book title using the book_id
    bookmarked_book = Book.objects.get(id=book_id).title

    # Call the recommend function
    recommended_books = recommend(bookmarked_book)

    # Render the recommended books in a template
    return render(request, 'authentication/recommendations.html', {'recommended_books': recommended_books})








