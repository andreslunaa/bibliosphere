# models.py

from django.db import models
from django.contrib.auth.models import User

# Genre model
class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

# UserProfile model to extend the built-in User model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_genres = models.ManyToManyField(Genre)

    def __str__(self):
        return self.user.username

# Book model
class Book(models.Model):
    title = models.CharField(max_length=255)
    series = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255)
    rating = models.FloatField(default=0.0, null=True, blank=True)
    description = models.TextField()
    isbn = models.CharField(max_length=150) 
    genres = models.ManyToManyField(Genre)
    characters = models.CharField(max_length=255, null=True, blank=True)
    pages = models.TextField()
    publisher = models.CharField(max_length=255, null=True, blank=True)
    awards = models.TextField(blank=True, null=True) 
    liked_percent = models.TextField(blank=True, null=True) 
    setting = models.TextField(blank=True, null=True)
    coverImg = models.TextField(blank=True, null=True)  

    def __str__(self):
        return f"{self.title} by {self.author}"
