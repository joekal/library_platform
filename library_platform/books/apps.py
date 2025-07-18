"""
Apps configuration for books.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BooksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'books'
    verbose_name = _('Books')
    
    def ready(self):
        import books.signals