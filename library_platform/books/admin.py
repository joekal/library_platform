"""
Admin configuration for books app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Genre, Author, Book, ReadingHistory, Review, BookCollection


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Admin for Genre model."""
    list_display = ('name', 'color', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    prepopulated_fields = {'name': ('name',)}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin for Author model."""
    list_display = ('get_full_name', 'nationality', 'birth_date', 'created_at')
    search_fields = ('first_name', 'last_name', 'nationality')
    list_filter = ('nationality', 'birth_date', 'created_at')
    fields = (
        ('first_name', 'last_name'),
        'bio',
        ('birth_date', 'death_date'),
        'nationality',
        'photo',
        'website'
    )


class ReviewInline(admin.TabularInline):
    """Inline admin for reviews."""
    model = Review
    extra = 0
    readonly_fields = ('created_at', 'helpful_votes')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin for Book model."""
    list_display = (
        'title', 'get_authors_display', 'language', 'status', 
        'average_rating', 'is_featured', 'created_at'
    )
    list_filter = (
        'status', 'language', 'is_featured', 'is_new', 
        'genres', 'publication_date', 'created_at'
    )
    search_fields = ('title', 'subtitle', 'isbn', 'authors__first_name', 'authors__last_name')
    filter_horizontal = ('authors', 'genres')
    readonly_fields = ('average_rating', 'total_ratings', 'view_count', 'download_count')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'subtitle', 'authors', 'genres', 'description')
        }),
        (_('Publication Details'), {
            'fields': ('isbn', 'language', 'pages', 'publisher', 'publication_date', 'edition')
        }),
        (_('Media Files'), {
            'fields': ('cover_image', 'pdf_file', 'epub_file', 'audio_file')
        }),
        (_('Platform Settings'), {
            'fields': ('status', 'is_featured', 'is_new', 'tags')
        }),
        (_('Statistics'), {
            'fields': ('average_rating', 'total_ratings', 'view_count', 'download_count'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ReviewInline]
    
    def get_authors_display(self, obj):
        return obj.get_authors_display()
    get_authors_display.short_description = _('Authors')


@admin.register(ReadingHistory)
class ReadingHistoryAdmin(admin.ModelAdmin):
    """Admin for ReadingHistory model."""
    list_display = ('user', 'book', 'status', 'progress_percentage', 'rating', 'updated_at')
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('user__email', 'book__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin for Review model."""
    list_display = ('user', 'book', 'rating', 'is_approved', 'is_featured', 'helpful_votes', 'created_at')
    list_filter = ('rating', 'is_approved', 'is_featured', 'created_at')
    search_fields = ('user__email', 'book__title', 'title', 'content')
    readonly_fields = ('helpful_votes', 'created_at', 'updated_at')
    
    actions = ['approve_reviews', 'feature_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = _('Approve selected reviews')
    
    def feature_reviews(self, request, queryset):
        queryset.update(is_featured=True)
    feature_reviews.short_description = _('Feature selected reviews')


@admin.register(BookCollection)
class BookCollectionAdmin(admin.ModelAdmin):
    """Admin for BookCollection model."""
    list_display = ('name', 'user', 'visibility', 'created_at')
    list_filter = ('visibility', 'created_at')
    search_fields = ('name', 'user__email', 'description')
    filter_horizontal = ('books',)