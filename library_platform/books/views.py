"""
Views for books app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.db.models import Q, Avg, Count
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, Genre, Author, Review, ReadingHistory, BookCollection
from .serializers import (
    BookSerializer, GenreSerializer, AuthorSerializer, 
    ReviewSerializer, ReadingHistorySerializer, BookCollectionSerializer
)
from .forms import ReviewForm
from .filters import BookFilter


class BookListView(ListView):
    """List view for books with filtering and search."""
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Book.objects.filter(status='available').prefetch_related('authors', 'genres')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(authors__first_name__icontains=search_query) |
                Q(authors__last_name__icontains=search_query) |
                Q(description__icontains=search_query)
            ).distinct()
        
        # Filter by genre
        genre_id = self.request.GET.get('genre')
        if genre_id:
            queryset = queryset.filter(genres__id=genre_id)
        
        # Filter by language
        language = self.request.GET.get('language')
        if language:
            queryset = queryset.filter(language=language)
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['title', '-title', 'average_rating', '-average_rating', 'publication_date', '-publication_date']:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        context['languages'] = Book.LANGUAGE_CHOICES
        context['current_search'] = self.request.GET.get('search', '')
        context['current_genre'] = self.request.GET.get('genre', '')
        context['current_language'] = self.request.GET.get('language', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        return context


class BookDetailView(DetailView):
    """Detail view for a single book."""
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'
    
    def get_object(self):
        obj = super().get_object()
        # Increment view count
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        
        # Get user's reading history for this book
        if self.request.user.is_authenticated:
            try:
                context['user_history'] = ReadingHistory.objects.get(
                    user=self.request.user, book=book
                )
            except ReadingHistory.DoesNotExist:
                context['user_history'] = None
        
        # Get reviews
        context['reviews'] = book.reviews.filter(is_approved=True).order_by('-created_at')[:10]
        context['review_form'] = ReviewForm()
        
        # Get similar books (same genres)
        context['similar_books'] = Book.objects.filter(
            genres__in=book.genres.all(),
            status='available'
        ).exclude(id=book.id).distinct()[:6]
        
        return context


class BookReaderView(LoginRequiredMixin, DetailView):
    """Book reader view for authenticated users."""
    model = Book
    template_name = 'books/book_reader.html'
    context_object_name = 'book'
    
    def get_object(self):
        obj = super().get_object()
        # Create or update reading history
        history, created = ReadingHistory.objects.get_or_create(
            user=self.request.user,
            book=obj,
            defaults={'status': 'reading'}
        )
        if created or history.status == 'wishlist':
            history.status = 'reading'
            history.save()
        return obj


class BookSearchView(ListView):
    """Advanced search view for books."""
    model = Book
    template_name = 'books/book_search.html'
    context_object_name = 'books'
    paginate_by = 20
    
    def get_queryset(self):
        form = BookFilter(self.request.GET, queryset=Book.objects.filter(status='available'))
        return form.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = BookFilter(self.request.GET, queryset=self.get_queryset())
        return context


class GenreListView(ListView):
    """List view for genres."""
    model = Genre
    template_name = 'books/genre_list.html'
    context_object_name = 'genres'


class GenreDetailView(DetailView):
    """Detail view for a genre with its books."""
    model = Genre
    template_name = 'books/genre_detail.html'
    context_object_name = 'genre'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.filter(
            genres=self.object, status='available'
        ).order_by('-average_rating')[:20]
        return context


class AuthorListView(ListView):
    """List view for authors."""
    model = Author
    template_name = 'books/author_list.html'
    context_object_name = 'authors'
    paginate_by = 20


class AuthorDetailView(DetailView):
    """Detail view for an author with their books."""
    model = Author
    template_name = 'books/author_detail.html'
    context_object_name = 'author'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.filter(
            authors=self.object, status='available'
        ).order_by('-publication_date')
        return context


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """Create view for book reviews."""
    model = Review
    form_class = ReviewForm
    template_name = 'books/review_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.book = get_object_or_404(Book, pk=self.kwargs['pk'])
        
        # Check if user already reviewed this book
        if Review.objects.filter(user=self.request.user, book=form.instance.book).exists():
            messages.error(self.request, _('You have already reviewed this book.'))
            return redirect('books:detail', pk=self.kwargs['pk'])
        
        response = super().form_valid(form)
        
        # Update book rating
        form.instance.book.update_rating()
        
        messages.success(self.request, _('Your review has been submitted.'))
        return response
    
    def get_success_url(self):
        return self.object.book.get_absolute_url()


# API Views
class BookViewSet(viewsets.ModelViewSet):
    """API viewset for books."""
    queryset = Book.objects.filter(status='available')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ['title', 'authors__first_name', 'authors__last_name', 'description']
    ordering_fields = ['title', 'average_rating', 'publication_date', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_to_reading_list(self, request, pk=None):
        """Add book to user's reading list."""
        book = self.get_object()
        status = request.data.get('status', 'wishlist')
        
        history, created = ReadingHistory.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={'status': status}
        )
        
        if not created:
            history.status = status
            history.save()
        
        return Response({'status': 'success', 'message': 'Book added to reading list'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def update_progress(self, request, pk=None):
        """Update reading progress."""
        book = self.get_object()
        progress = request.data.get('progress', 0)
        current_page = request.data.get('current_page', 0)
        
        history, created = ReadingHistory.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={'status': 'reading'}
        )
        
        history.progress_percentage = progress
        history.current_page = current_page
        if progress >= 100:
            history.status = 'completed'
        history.save()
        
        return Response({'status': 'success', 'progress': progress})


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for genres."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for authors."""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'nationality']
    ordering_fields = ['last_name', 'first_name']
    ordering = ['last_name', 'first_name']


class ReviewViewSet(viewsets.ModelViewSet):
    """API viewset for reviews."""
    queryset = Review.objects.filter(is_approved=True)
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['book', 'rating']
    ordering_fields = ['created_at', 'rating', 'helpful_votes']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReadingHistoryViewSet(viewsets.ModelViewSet):
    """API viewset for reading history."""
    serializer_class = ReadingHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'rating']
    ordering_fields = ['updated_at', 'created_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        return ReadingHistory.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookCollectionViewSet(viewsets.ModelViewSet):
    """API viewset for book collections."""
    serializer_class = BookCollectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return BookCollection.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FeaturedBooksAPIView(APIView):
    """API view for featured books."""
    
    def get(self, request):
        books = Book.objects.filter(is_featured=True, status='available')[:10]
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


class NewReleasesAPIView(APIView):
    """API view for new releases."""
    
    def get(self, request):
        books = Book.objects.filter(is_new=True, status='available').order_by('-created_at')[:10]
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


class PopularBooksAPIView(APIView):
    """API view for popular books."""
    
    def get(self, request):
        books = Book.objects.filter(status='available').order_by('-average_rating', '-total_ratings')[:10]
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)