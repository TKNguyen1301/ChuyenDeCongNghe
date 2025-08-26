"""
Django Forms for Templates Practice
"""
from django import forms
from django.contrib.auth.models import User
from .models import Comment, Newsletter, Post, Author


class CommentForm(forms.ModelForm):
    """Form for adding comments to posts."""
    
    class Meta:
        model = Comment
        fields = ['author_name', 'author_email', 'author_website', 'content']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name',
                'required': True
            }),
            'author_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your email',
                'required': True
            }),
            'author_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your website (optional)'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your comment here...',
                'required': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author_website'].required = False


class NewsletterForm(forms.ModelForm):
    """Form for newsletter subscription."""
    
    class Meta:
        model = Newsletter
        fields = ['email', 'name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
                'required': True
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name (optional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False


class PostForm(forms.ModelForm):
    """Form for creating/editing posts."""
    
    class Meta:
        model = Post
        fields = [
            'title', 'content', 'excerpt', 'category', 'tags', 
            'status', 'featured', 'allow_comments'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Post title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Write your post content here...'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief excerpt (optional)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tags': forms.CheckboxSelectMultiple(),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_comments': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class SearchForm(forms.Form):
    """Advanced search form."""
    
    q = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    tag = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Tags",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    author = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="All Authors",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    order_by = forms.ChoiceField(
        choices=[
            ('-published_at', 'Newest First'),
            ('published_at', 'Oldest First'),
            ('-view_count', 'Most Popular'),
            ('title', 'Title A-Z'),
        ],
        required=False,
        initial='-published_at',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    def __init__(self, *args, **kwargs):
        from .models import Category, Tag, Author
        super().__init__(*args, **kwargs)
        
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['tag'].queryset = Tag.objects.all()
        self.fields['author'].queryset = Author.objects.all()


class ContactForm(forms.Form):
    """Contact form example."""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email'
        })
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Your message'
        })
    )
    
    def send_email(self):
        """Send contact email (demo only)."""
        # In a real app, you would send an actual email here
        pass


class FilterForm(forms.Form):
    """Form for filtering content."""
    
    FILTER_CHOICES = [
        ('all', 'All Posts'),
        ('featured', 'Featured'),
        ('recent', 'Recent'),
        ('popular', 'Popular'),
    ]
    
    filter_type = forms.ChoiceField(
        choices=FILTER_CHOICES,
        required=False,
        initial='all',
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
