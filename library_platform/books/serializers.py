"""
Serializers for books app.
"""
from rest_framework import serializers
from .models import Book, Genre, Author, Review, ReadingHistory, BookCollection


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for Genre model."""
    
    class Meta:
        model = Genre
        fields = ['id', 'name', 'description', 'color']


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Author model."""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'bio',
            'birth_date', 'death_date', 'nationality', 'photo', 'website'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model."""
    
    authors = AuthorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    authors_display = serializers.SerializerMethodField()
    genres_display = serializers.SerializerMethodField()
    has_audio = serializers.SerializerMethodField()
    has_ebook = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'subtitle', 'authors', 'genres', 'description',
            'isbn', 'language', 'pages', 'cover_image', 'pdf_file', 'epub_file',
            'audio_file', 'publisher', 'publication_date', 'edition', 'status',
            'is_featured', 'is_new', 'average_rating', 'total_ratings',
            'view_count', 'download_count', 'tags', 'created_at', 'updated_at',
            'authors_display', 'genres_display', 'has_audio', 'has_ebook'
        ]
        read_only_fields = [
            'average_rating', 'total_ratings', 'view_count', 'download_count',
            'created_at', 'updated_at'
        ]
    
    def get_authors_display(self, obj):
        return obj.get_authors_display()
    
    def get_genres_display(self, obj):
        return obj.get_genres_display()
    
    def get_has_audio(self, obj):
        return obj.has_audio()
    
    def get_has_ebook(self, obj):
        return obj.has_ebook()


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""
    
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_name', 'book', 'title', 'content', 'rating',
            'is_approved', 'is_featured', 'helpful_votes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'is_approved', 'is_featured', 'helpful_votes',
            'created_at', 'updated_at'
        ]
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class ReadingHistorySerializer(serializers.ModelSerializer):
    """Serializer for ReadingHistory model."""
    
    book_title = serializers.SerializerMethodField()
    book_cover = serializers.SerializerMethodField()
    
    class Meta:
        model = ReadingHistory
        fields = [
            'id', 'user', 'book', 'book_title', 'book_cover', 'status',
            'progress_percentage', 'current_page', 'rating', 'notes',
            'started_reading', 'finished_reading', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_book_title(self, obj):
        return obj.book.title
    
    def get_book_cover(self, obj):
        if obj.book.cover_image:
            return obj.book.cover_image.url
        return None


class BookCollectionSerializer(serializers.ModelSerializer):
    """Serializer for BookCollection model."""
    
    books_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BookCollection
        fields = [
            'id', 'user', 'name', 'description', 'books', 'books_count',
            'visibility', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_books_count(self, obj):
        return obj.books.count()