# forms.py
from django import forms
from .models import UserProfile, Genre

# List of common genres (you can update this list as needed)
COMMON_GENRES = [
    'Action', 'Adventure', 'Classics', 'Comic Book', 'Detective',
    'Mystery', 'Fantasy', 'Historical Fiction', 'Horror', 'Literary Fiction',
    'Romance', 'Science Fiction', 'Short Stories', 'Thrillers', 'Biographies'
]


class PreferredGenresForm(forms.ModelForm):
    preferred_genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # This should ensure it uses checkboxes
        required=False
    )
    
    class Meta:
        model = UserProfile
        fields = ['preferred_genres']

    def __init__(self, *args, **kwargs):
        super(PreferredGenresForm, self).__init__(*args, **kwargs)
        # Set the queryset to include only common genres + the user's selected genres
        self.fields['preferred_genres'].queryset = Genre.objects.filter(
            name__in=COMMON_GENRES
        ) | Genre.objects.filter(
            id__in=self.instance.preferred_genres.values_list('id', flat=True)
        )
