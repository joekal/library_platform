"""
Filters for books app.
"""
import django_filters
from django.utils.translation import gettext_lazy as _
from django.db import models  # Ajouté pour utiliser models.Q
from .models import Book, Genre, Author


class BookFilter(django_filters.FilterSet):
    """Filter for books with advanced options."""
    
    title = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label=_('Title')
    )
    
    author = django_filters.ModelChoiceFilter(
        field_name='authors',
        queryset=Author.objects.all(),
        label=_('Author')
    )
    
    genre = django_filters.ModelMultipleChoiceFilter(
        field_name='genres',
        queryset=Genre.objects.all(),
        label=_('Genres')
    )
    
    language = django_filters.ChoiceFilter(
        field_name='language',
        choices=Book.LANGUAGE_CHOICES,
        label=_('Language')
    )
    
    min_rating = django_filters.NumberFilter(
        field_name='average_rating',
        lookup_expr='gte',
        label=_('Minimum rating')
    )
    
    max_pages = django_filters.NumberFilter(
        field_name='pages',
        lookup_expr='lte',
        label=_('Maximum pages')
    )
    
    has_audio = django_filters.BooleanFilter(
        method='filter_has_audio',
        label=_('Has audio')
    )
    
    has_ebook = django_filters.BooleanFilter(
        method='filter_has_ebook',
        label=_('Has e-book')
    )
    
    publication_year = django_filters.NumberFilter(
        field_name='publication_date__year',
        label=_('Publication year')
    )
    
    is_featured = django_filters.BooleanFilter(
        field_name='is_featured',
        label=_('Featured')
    )
    
    is_new = django_filters.BooleanFilter(
        field_name='is_new',
        label=_('New release')
    )
    
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'genre', 'language', 'min_rating',
            'max_pages', 'has_audio', 'has_ebook', 'publication_year',
            'is_featured', 'is_new'
        ]
    
    def filter_has_audio(self, queryset, name, value):
        """Filter books that have audio files."""
        if value:
            return queryset.exclude(audio_file='')
        return queryset
    
    def filter_has_ebook(self, queryset, name, value):
        """Filter books that have e-book files."""
        if value:
            return queryset.filter(
                models.Q(pdf_file__isnull=False) | models.Q(epub_file__isnull=False)
            ).exclude(pdf_file='').exclude(epub_file='')