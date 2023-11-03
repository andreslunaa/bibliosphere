from django.contrib import admin
from django.urls import include, path
from . import views
#urls.py
urlpatterns = [
    path('', views.home, name = 'home'),
    path('signup', views.signup, name ='signup'),
    path('signin', views.signin, name ='signin'),
    path('signout', views.signout, name ='signout'),
    path('activate/<uidb64>/<token>', views.activate, name ='activate'),
    #Access user's personal information
    path('saved_information/', views.saved_information, name='saved_information'),
    # Add Preferred Genres
    path('preferred_genres/', views.preferred_genres, name='preferred_genres'),
    path('search_genres/', views.search_genres, name='search_genres'),
    path('search_genres2/', views.search_and_select_genres, name='search_genres2'),
    # Drop Preferred Genres
    path('drop_preferred_genres/', views.drop_preferred_genres, name='drop_preferred_genres'),
    # Edit User Info
    path('edit_info/', views.edit_user_info, name='edit_user_info'),
    # Specific book link
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
]