"""
Views for core app - main pages and functionality.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
from books.models import Book, Genre
from groups.models import ReadingGroup
from recommendations.models import Recommendation


class HomeView(TemplateView):
    """Home page view with featured content."""
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured books
        context['featured_books'] = Book.objects.filter(
            is_featured=True, status='available'
        ).prefetch_related('authors', 'genres')[:6]
        
        # New releases
        context['new_releases'] = Book.objects.filter(
            is_new=True, status='available'
        ).order_by('-created_at').prefetch_related('authors', 'genres')[:6]
        
        # Popular books (by rating)
        context['popular_books'] = Book.objects.filter(
            status='available'
        ).order_by('-average_rating', '-total_ratings').prefetch_related('authors', 'genres')[:6]
        
        # Active reading groups
        context['active_groups'] = ReadingGroup.objects.filter(
            is_active=True
        ).annotate(member_count=Count('members')).order_by('-member_count')[:4]
        
        # User recommendations if authenticated
        if self.request.user.is_authenticated:
            context['user_recommendations'] = Recommendation.objects.filter(
                user=self.request.user,
                is_active=True
            ).order_by('-confidence_score')[:4]
        
        # Statistics
        context['stats'] = {
            'total_books': Book.objects.filter(status='available').count(),
            'total_genres': Genre.objects.count(),
            'total_groups': ReadingGroup.objects.filter(is_active=True).count(),
        }
        
        return context


class AboutView(TemplateView):
    """About page view."""
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['features'] = [
            {
                'icon': 'fas fa-book-open',
                'title': _('Interactive Library'),
                'description': _('Access thousands of books, documents, and audio content in multiple formats.')
            },
            {
                'icon': 'fas fa-brain',
                'title': _('AI Recommendations'),
                'description': _('Get personalized book suggestions powered by advanced AI algorithms.')
            },
            {
                'icon': 'fas fa-globe',
                'title': _('Multilingual'),
                'description': _('Enjoy content and interface in multiple languages with seamless switching.')
            },
            {
                'icon': 'fas fa-volume-up',
                'title': _('Audio Integration'),
                'description': _('Listen to audiobooks or use text-to-speech for any content.')
            },
            {
                'icon': 'fas fa-universal-access',
                'title': _('Accessibility'),
                'description': _('Designed for everyone with contrast options, keyboard navigation, and dyslexia support.')
            },
            {
                'icon': 'fas fa-users',
                'title': _('Social Collaboration'),
                'description': _('Join reading groups, share comments, and connect with fellow readers.')
            }
        ]
        return context


class ContactView(TemplateView):
    """Contact page view."""
    template_name = 'core/contact.html'


class AccessibilityView(TemplateView):
    """Accessibility information page."""
    template_name = 'core/accessibility.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accessibility_features'] = [
            {
                'category': _('Visual Accessibility'),
                'features': [
                    _('High contrast themes'),
                    _('Adjustable font sizes'),
                    _('Dyslexia-friendly fonts'),
                    _('Color-blind friendly design'),
                ]
            },
            {
                'category': _('Motor Accessibility'),
                'features': [
                    _('Full keyboard navigation'),
                    _('Large click targets'),
                    _('Reduced motion options'),
                    _('Voice control support'),
                ]
            },
            {
                'category': _('Cognitive Accessibility'),
                'features': [
                    _('Clear navigation structure'),
                    _('Simple language options'),
                    _('Progress indicators'),
                    _('Consistent layout'),
                ]
            },
            {
                'category': _('Auditory Accessibility'),
                'features': [
                    _('Screen reader support'),
                    _('Audio descriptions'),
                    _('Text-to-speech'),
                    _('Visual indicators for audio'),
                ]
            }
        ]
        return context