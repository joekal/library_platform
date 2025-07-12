"""
URL configuration for books app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API URLs
router = DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'genres', views.GenreViewSet)
router.register(r'authors', views.AuthorViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'reading-history', views.ReadingHistoryViewSet)
router.register(r'collections', views.BookCollectionViewSet)

app_name = 'books'

urlpatterns = [
    # Web views
    path('', views.BookListView.as_view(), name='list'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='detail'),
    path('<int:pk>/read/', views.BookReaderView.as_view(), name='read'),
    path('<int:pk>/review/', views.ReviewCreateView.as_view(), name='review'),
    path('search/', views.BookSearchView.as_view(), name='search'),
    path('genres/', views.GenreListView.as_view(), name='genres'),
    path('genres/<int:pk>/', views.GenreDetailView.as_view(), name='genre_detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/featured/', views.FeaturedBooksAPIView.as_view(), name='api_featured'),
    path('api/new-releases/', views.NewReleasesAPIView.as_view(), name='api_new_releases'),
    path('api/popular/', views.PopularBooksAPIView.as_view(), name='api_popular'),
]