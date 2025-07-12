"""
Forms for books app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column
from .models import Review, BookCollection, Book


class ReviewForm(forms.ModelForm):
    """Form for creating book reviews."""
    
    class Meta:
        model = Review
        fields = ['title', 'content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
            'rating': forms.Select(choices=[(i, f'{i} ⭐') for i in range(1, 6)]),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'rating',
            'content',
            Submit('submit', _('Submit Review'), css_class='btn btn-primary')
        )


class BookCollectionForm(forms.ModelForm):
    """Form for creating book collections."""
    
    class Meta:
        model = BookCollection
        fields = ['name', 'description', 'visibility']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'description',
            'visibility',
            Submit('submit', _('Create Collection'), css_class='btn btn-success')
        )


class BookSearchForm(forms.Form):
    """Advanced search form for books."""
    
    query = forms.CharField(
        label=_('Search'),
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Title, author, description...')})
    )
    
    genre = forms.ModelChoiceField(
        label=_('Genre'),
        queryset=None,  # Will be set in __init__
        required=False,
        empty_label=_('All genres')
    )
    
    language = forms.ChoiceField(
        label=_('Language'),
        choices=[('', _('All languages'))] + list(Book.LANGUAGE_CHOICES),
        required=False
    )
    
    has_audio = forms.BooleanField(
        label=_('Has audio'),
        required=False
    )
    
    has_ebook = forms.BooleanField(
        label=_('Has e-book'),
        required=False
    )
    
    min_rating = forms.ChoiceField(
        label=_('Minimum rating'),
        choices=[('', _('Any rating'))] + [(i, f'{i}+ ⭐') for i in range(1, 5)],
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Genre
        self.fields['genre'].queryset = Genre.objects.all()

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('query', css_class='form-group col-md-6 mb-0'),
                Column('genre', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('language', css_class='form-group col-md-4 mb-0'),
                Column('min_rating', css_class='form-group col-md-4 mb-0'),
                Column(
                    'has_audio',
                    'has_ebook',
                    css_class='form-group col-md-4 mb-0'
                ),
                css_class='form-row'
            ),
            Submit('submit', _('Search'), css_class='btn btn-primary')
        )