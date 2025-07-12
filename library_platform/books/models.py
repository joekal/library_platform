"""
Models for books and library management.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from taggit.managers import TaggableManager
from tinymce.models import HTMLField

User = get_user_model()


class Genre(models.Model):
    """Book genre model."""
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    color = models.CharField(_('color'), max_length=7, default='#3B82F6')  # Hex color
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Author(models.Model):
    """Author model."""
    
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    bio = HTMLField(_('biography'), blank=True)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    death_date = models.DateField(_('death date'), blank=True, null=True)
    nationality = models.CharField(_('nationality'), max_length=100, blank=True)
    photo = models.ImageField(_('photo'), upload_to='authors/', blank=True, null=True)
    website = models.URLField(_('website'), blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Author')
        verbose_name_plural = _('Authors')
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    """Book model with multilingual support."""
    
    LANGUAGE_CHOICES = [
        ('fr', _('French')),
        ('en', _('English')),
        ('es', _('Spanish')),
        ('de', _('German')),
        ('it', _('Italian')),
    ]
    
    STATUS_CHOICES = [
        ('available', _('Available')),
        ('unavailable', _('Unavailable')),
        ('coming_soon', _('Coming Soon')),
    ]
    
    # Basic information
    title = models.CharField(_('title'), max_length=200)
    subtitle = models.CharField(_('subtitle'), max_length=200, blank=True)
    authors = models.ManyToManyField(Author, verbose_name=_('authors'))
    genres = models.ManyToManyField(Genre, verbose_name=_('genres'))
    
    # Content
    description = HTMLField(_('description'))
    isbn = models.CharField(_('ISBN'), max_length=17, unique=True, blank=True, null=True)
    language = models.CharField(_('language'), max_length=5, choices=LANGUAGE_CHOICES, default='fr')
    pages = models.PositiveIntegerField(_('pages'), default=0)
    
    # Media files
    cover_image = models.ImageField(_('cover image'), upload_to='book_covers/')
    pdf_file = models.FileField(_('PDF file'), upload_to='books/pdf/', blank=True, null=True)
    epub_file = models.FileField(_('EPUB file'), upload_to='books/epub/', blank=True, null=True)
    audio_file = models.FileField(_('audio file'), upload_to='books/audio/', blank=True, null=True)
    
    # Publication info
    publisher = models.CharField(_('publisher'), max_length=200, blank=True)
    publication_date = models.DateField(_('publication date'))
    edition = models.CharField(_('edition'), max_length=100, blank=True)
    
    # Platform specific
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='available')
    is_featured = models.BooleanField(_('featured'), default=False)
    is_new = models.BooleanField(_('new release'), default=False)
    
    # Ratings and stats
    average_rating = models.DecimalField(_('average rating'), max_digits=3, decimal_places=2, default=0)
    total_ratings = models.PositiveIntegerField(_('total ratings'), default=0)
    view_count = models.PositiveIntegerField(_('view count'), default=0)
    download_count = models.PositiveIntegerField(_('download count'), default=0)
    
    # SEO and tags
    tags = TaggableManager(verbose_name=_('tags'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Book')
        verbose_name_plural = _('Books')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['language']),
            models.Index(fields=['status']),
            models.Index(fields=['-average_rating']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('books:detail', kwargs={'pk': self.pk})
    
    def get_authors_display(self):
        """Return comma-separated list of authors."""
        return ", ".join([author.get_full_name() for author in self.authors.all()])
    
    def get_genres_display(self):
        """Return comma-separated list of genres."""
        return ", ".join([genre.name for genre in self.genres.all()])
    
    def has_audio(self):
        """Check if book has audio file."""
        return bool(self.audio_file)
    
    def has_ebook(self):
        """Check if book has digital files."""
        return bool(self.pdf_file or self.epub_file)
    
    def update_rating(self):
        """Update average rating based on reviews."""
        reviews = self.reviews.all()
        if reviews:
            total = sum([review.rating for review in reviews])
            self.average_rating = total / len(reviews)
            self.total_ratings = len(reviews)
            self.save(update_fields=['average_rating', 'total_ratings'])


class ReadingHistory(models.Model):
    """Track user reading history and progress."""
    
    STATUS_CHOICES = [
        ('wishlist', _('Wishlist')),
        ('reading', _('Currently Reading')),
        ('completed', _('Completed')),
        ('abandoned', _('Abandoned')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_history')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='readers')
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='wishlist')
    
    # Progress tracking
    progress_percentage = models.PositiveIntegerField(_('progress percentage'), default=0)
    current_page = models.PositiveIntegerField(_('current page'), default=0)
    
    # User feedback
    rating = models.PositiveIntegerField(
        _('rating'), 
        choices=[(i, i) for i in range(1, 6)], 
        blank=True, 
        null=True
    )
    notes = models.TextField(_('personal notes'), blank=True)
    
    # Timestamps
    started_reading = models.DateTimeField(_('started reading'), blank=True, null=True)
    finished_reading = models.DateTimeField(_('finished reading'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Reading History')
        verbose_name_plural = _('Reading Histories')
        unique_together = ['user', 'book']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.book.title} ({self.status})"


class Review(models.Model):
    """Book reviews and comments."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    
    title = models.CharField(_('title'), max_length=200, blank=True)
    content = models.TextField(_('content'))
    rating = models.PositiveIntegerField(_('rating'), choices=[(i, i) for i in range(1, 6)])
    
    # Moderation
    is_approved = models.BooleanField(_('approved'), default=True)
    is_featured = models.BooleanField(_('featured'), default=False)
    
    # Interaction
    helpful_votes = models.PositiveIntegerField(_('helpful votes'), default=0)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        unique_together = ['user', 'book']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.book.title} ({self.rating}/5)"


class BookCollection(models.Model):
    """User-created book collections/lists."""
    
    VISIBILITY_CHOICES = [
        ('private', _('Private')),
        ('public', _('Public')),
        ('friends', _('Friends Only')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    books = models.ManyToManyField(Book, verbose_name=_('books'), blank=True)
    
    visibility = models.CharField(
        _('visibility'), 
        max_length=20, 
        choices=VISIBILITY_CHOICES, 
        default='private'
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Book Collection')
        verbose_name_plural = _('Book Collections')
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"