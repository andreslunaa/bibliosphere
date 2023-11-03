from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage

from . tokens import generater_token
from . import views
from bibliosphere import settings

from .models import Book, UserProfile, Genre
import random
from django.db.models import Subquery
from django.http import JsonResponse
from django.db import IntegrityError
# --------------------------------------------------------------------------------

def home(request):
    query = request.GET.get('search')
    books_by_genre = {}
    available_genres = list(Genre.objects.values_list('name', flat=True))

    if query:
        books = Book.objects.filter(title__icontains=query)
        return render(request, 'authentication/index.html', {'books': books})
    else:
        # Determine the genres to display
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user=request.user)
            selected_genres = list(user_profile.preferred_genres.values_list('name', flat=True))
            
            # Fill up with random genres if less than 5 preferred genres
            random.shuffle(available_genres)
            for genre in available_genres:
                if len(selected_genres) >= 5:
                    break
                if genre not in selected_genres:
                    selected_genres.append(genre)
        else:
            # Select 5 random genres for non-authenticated users
            random.shuffle(available_genres)
            selected_genres = available_genres[:5]
        
        # Get 7 random books for each genre
        for genre_name in selected_genres:
            # Get Books in the current genre
            genre_books_qs = Book.objects.filter(genres__name=genre_name)

            # Get 7 random books IDs
            random_books_ids = genre_books_qs.order_by('?').values('id')[:7]

            # Get the actual Book objects for the collected IDs
            genre_books = Book.objects.filter(id__in=Subquery(random_books_ids))

            books_by_genre[genre_name] = genre_books

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
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            user.is_active = False
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
            #find books based on liked genres! --> important for the future!!!!!
            books_by_genre = find_books(request)
            return render(request,'authentication/index.html', {'books_by_genre': books_by_genre})
        else:
            messages.error(request, "Invalid Credentials!")
            return redirect('home')
    return render(request,'authentication/signin.html')

def signout(request):
    #usname = request.user.username
    #set_genres(usname)
    logout(request)
    messages.success(request, "You have been successfully signed out!")
    return redirect('home')

def find_books(request):
    books = []
    books_by_genre = {}
    available_genres = ['Adventure', 'Classic', 'Thriller', 'Romance', 'Science Fiction', 'Mystery', 'Fantasy', 'History']

    # Get preferred_genres from UserProfile
    user_profile = UserProfile.objects.get(user=request.user)
    selected_genres = list(user_profile.preferred_genres.values_list('name', flat=True))
    
    # If selected genres are less than 5, fill up with random genres from the available list
    while len(selected_genres) < 5:
        random_genre = random.choice(available_genres)
        if random_genre not in selected_genres:
            selected_genres.append(random_genre)

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
        login(request, user) 
        return render(request,'authentication/index.html', { 'fname': user.first_name })
    else:
        return render(request,'activation_failed.html')

def saved_information(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    preferred_genres = user_profile.preferred_genres.all().order_by('name')
    return render(request, 'authentication/saved_information.html', {
        'user': request.user,
        'preferred_genres': preferred_genres
    })

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

def search_genres(request):
    if 'term' in request.GET:
        qs = Genre.objects.filter(name__icontains=request.GET.get('term'))
        genres = list(qs.values('id', 'name'))
        return JsonResponse(genres, safe=False)
    return JsonResponse([], safe=False)

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

        return redirect('saved_information')  # Replace with your appropriate view name

    return render(request, 'authentication/edit_info.html')

def book_detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    print (book.title)
    return render(request, 'authentication/book_detail.html', {'book': book})
