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
    path('search_genres2/', views.search_and_select_genres, name='search_genres2'),
    # Drop Preferred Genres
    path('drop_preferred_genres/', views.drop_preferred_genres, name='drop_preferred_genres'),
    # Edit User Info
    path('edit_info/', views.edit_user_info, name='edit_user_info'),
    # Specific book link
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('add-bookmark/<int:book_id>/', views.add_bookmark, name='add_bookmark'),
    path('bookmarks/', views.list_bookmarks, name='list_bookmarks'),
    path('remove-bookmark/<int:book_id>/', views.remove_bookmark, name='remove_bookmark'),
    path('add-comment/<int:book_id>/', views.add_comment, name='add_comment'),
    path('user-comments/', views.user_comments, name='user_comments'),
    path('add-rating/<int:book_id>/', views.add_rating, name='add_rating'),
    path('user-ratings/', views.user_ratings, name='user_ratings'),
    path('recommendations/<int:book_id>/', views.recommendation_view, name='recommendations'),

]