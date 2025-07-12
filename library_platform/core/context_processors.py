"""
Context processors for core app.
"""
from django.conf import settings


def accessibility_settings(request):
    """Add accessibility settings to template context."""
    context = {}
    
    if request.user.is_authenticated:
        context.update({
            'user_font_size': request.user.font_size,
            'user_theme': request.user.theme,
            'user_dyslexic_font': request.user.dyslexic_font,
            'user_audio_enabled': request.user.audio_enabled,
        })
    else:
        context.update({
            'user_font_size': 'medium',
            'user_theme': 'light',
            'user_dyslexic_font': False,
            'user_audio_enabled': True,
        })
    
    return context