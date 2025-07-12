"""
Signals for books app.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review


@receiver(post_save, sender=Review)
def update_book_rating_on_review_save(sender, instance, **kwargs):
    """Update book rating when a review is saved."""
    instance.book.update_rating()


@receiver(post_delete, sender=Review)
def update_book_rating_on_review_delete(sender, instance, **kwargs):
    """Update book rating when a review is deleted."""
    instance.book.update_rating()