"""
Management command to create sample data for templates practice.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
import random
from datetime import timedelta

from templates_practice.models import (
    Category, Tag, Author, Post, Comment, Newsletter, TemplateExample
)


class Command(BaseCommand):
    help = 'Create sample data for templates practice'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data'
        )
        parser.add_argument(
            '--posts',
            type=int,
            default=20,
            help='Number of posts to create (default: 20)'
        )
        parser.add_argument(
            '--comments',
            type=int,
            default=50,
            help='Number of comments to create (default: 50)'
        )
    
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()
        
        self.stdout.write('Creating sample data...')
        
        # Create users and authors
        authors = self.create_authors()
        
        # Create categories
        categories = self.create_categories()
        
        # Create tags
        tags = self.create_tags()
        
        # Create posts
        posts = self.create_posts(authors, categories, tags, options['posts'])
        
        # Create comments
        self.create_comments(posts, options['comments'])
        
        # Create newsletter subscriptions
        self.create_newsletter_subscriptions()
        
        # Create template examples
        self.create_template_examples()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data with {len(posts)} posts'
            )
        )
    
    def clear_data(self):
        """Clear existing data."""
        Post.objects.all().delete()
        Comment.objects.all().delete()
        Author.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        Newsletter.objects.all().delete()
        TemplateExample.objects.all().delete()
    
    def create_authors(self):
        """Create sample authors."""
        authors_data = [
            ('john_doe', 'John', 'Doe', 'john@example.com', 'Full-stack developer passionate about Django and Python.'),
            ('jane_smith', 'Jane', 'Smith', 'jane@example.com', 'Frontend specialist with expertise in modern web technologies.'),
            ('mike_johnson', 'Mike', 'Johnson', 'mike@example.com', 'Backend developer focused on scalable web applications.'),
            ('sarah_wilson', 'Sarah', 'Wilson', 'sarah@example.com', 'Technical writer and Django enthusiast.'),
            ('david_brown', 'David', 'Brown', 'david@example.com', 'DevOps engineer with Python automation expertise.'),
        ]
        
        authors = []
        for username, first_name, last_name, email, bio in authors_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'is_active': True,
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
            
            author, _ = Author.objects.get_or_create(
                user=user,
                defaults={
                    'bio': bio,
                    'website': f'https://{username}.dev',
                    'birth_date': timezone.now().date() - timedelta(days=random.randint(7300, 14600)),
                    'social_media': {
                        'twitter': f'@{username}',
                        'github': f'https://github.com/{username}',
                        'linkedin': f'https://linkedin.com/in/{username}'
                    }
                }
            )
            authors.append(author)
        
        return authors
    
    def create_categories(self):
        """Create sample categories."""
        categories_data = [
            ('Django Basics', 'Introduction to Django framework and core concepts'),
            ('Templates', 'Django template system, filters, tags, and inheritance'),
            ('Models & ORM', 'Database models, queries, and ORM techniques'),
            ('Views & URLs', 'View functions, class-based views, and URL patterns'),
            ('Forms', 'Django forms, validation, and form handling'),
            ('Authentication', 'User authentication, permissions, and security'),
            ('Deployment', 'Deploying Django applications to production'),
            ('Best Practices', 'Django coding standards and best practices'),
            ('Advanced Topics', 'Advanced Django features and techniques'),
            ('Third-party Packages', 'Useful Django packages and integrations'),
        ]
        
        categories = []
        for name, description in categories_data:
            category, _ = Category.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'description': description,
                    'is_active': True,
                }
            )
            categories.append(category)
        
        return categories
    
    def create_tags(self):
        """Create sample tags."""
        tag_names = [
            'python', 'django', 'web-development', 'backend', 'frontend',
            'api', 'rest', 'database', 'postgresql', 'mysql', 'sqlite',
            'html', 'css', 'javascript', 'bootstrap', 'responsive',
            'authentication', 'security', 'testing', 'deployment',
            'docker', 'nginx', 'gunicorn', 'celery', 'redis',
            'beginner', 'intermediate', 'advanced', 'tutorial', 'guide'
        ]
        
        colors = [
            '#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8',
            '#6f42c1', '#e83e8c', '#fd7e14', '#20c997', '#6c757d'
        ]
        
        tags = []
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'color': random.choice(colors),
                }
            )
            tags.append(tag)
        
        return tags
    
    def create_posts(self, authors, categories, tags, count):
        """Create sample posts."""
        post_titles = [
            'Getting Started with Django Templates',
            'Understanding Django Template Inheritance',
            'Custom Template Filters and Tags',
            'Context Processors in Django',
            'Template Loading and Rendering',
            'Building Reusable Template Components',
            'Django Template Best Practices',
            'Advanced Template Techniques',
            'Template Security and Safety',
            'Debugging Django Templates',
            'Template Performance Optimization',
            'Using Jinja2 with Django',
            'Template Testing Strategies',
            'Internationalization in Templates',
            'Template Caching Techniques',
            'Building a Template Library',
            'Template Design Patterns',
            'Responsive Templates with Bootstrap',
            'AJAX and Dynamic Templates',
            'Template Error Handling',
            'Template Variables and Context',
            'Template Tags Deep Dive',
            'Custom Template Libraries',
            'Template Engine Configuration',
            'Template Debugging Techniques',
        ]
        
        sample_content = [
            "Django templates provide a powerful way to generate dynamic HTML content. In this comprehensive guide, we'll explore the various features and capabilities of the Django template system.",
            "Template inheritance is one of the most powerful features of Django templates. It allows you to build a base template that contains common elements and extend it in child templates.",
            "Custom template filters and tags enable you to extend Django's template functionality. They provide a way to add custom logic and formatting to your templates.",
            "Context processors automatically add variables to the template context. They're useful for adding common data that should be available in all templates.",
            "Understanding how Django loads and renders templates is crucial for optimizing performance and debugging template issues.",
        ]
        
        posts = []
        for i in range(count):
            title = post_titles[i % len(post_titles)]
            if i >= len(post_titles):
                title = f"{title} - Part {(i // len(post_titles)) + 1}"
            
            # Generate content
            content_parts = []
            for j in range(random.randint(3, 8)):
                content_parts.append(sample_content[j % len(sample_content)] + f" This is paragraph {j+1} of the article.")
            
            content = '\n\n'.join(content_parts)
            
            post = Post.objects.create(
                title=title,
                slug=slugify(title) + f'-{i+1}',
                content=content,
                excerpt=content_parts[0][:300] + '...',
                author=random.choice(authors),
                category=random.choice(categories),
                status=random.choice([Post.PUBLISHED, Post.PUBLISHED, Post.PUBLISHED, Post.DRAFT]),
                featured=random.choice([True, False, False, False, False]),
                allow_comments=True,
                published_at=timezone.now() - timedelta(days=random.randint(1, 365)),
                view_count=random.randint(10, 1000),
            )
            
            # Add random tags
            post_tags = random.sample(tags, random.randint(2, 6))
            post.tags.set(post_tags)
            
            posts.append(post)
        
        return posts
    
    def create_comments(self, posts, count):
        """Create sample comments."""
        comment_authors = [
            ('Alice Johnson', 'alice@example.com'),
            ('Bob Smith', 'bob@example.com'),
            ('Carol Davis', 'carol@example.com'),
            ('Dan Wilson', 'dan@example.com'),
            ('Eva Brown', 'eva@example.com'),
            ('Frank Miller', 'frank@example.com'),
            ('Grace Lee', 'grace@example.com'),
            ('Henry Taylor', 'henry@example.com'),
        ]
        
        comment_templates = [
            "Great article! Thanks for sharing this information.",
            "This is exactly what I was looking for. Very helpful!",
            "Excellent explanation. I learned a lot from this post.",
            "Could you provide more examples for this topic?",
            "I have a question about the implementation...",
            "This approach worked perfectly for my project.",
            "Thanks for the detailed tutorial. Very clear and easy to follow.",
            "I would love to see more content like this.",
            "Amazing work! Keep it up.",
            "This solved my problem. Thank you so much!",
        ]
        
        published_posts = [p for p in posts if p.status == Post.PUBLISHED]
        
        for i in range(count):
            post = random.choice(published_posts)
            author_name, author_email = random.choice(comment_authors)
            
            Comment.objects.create(
                post=post,
                author_name=author_name,
                author_email=author_email,
                content=random.choice(comment_templates) + f" (Comment {i+1})",
                is_approved=random.choice([True, True, True, False]),
                is_spam=random.choice([False, False, False, False, True]),
                created_at=timezone.now() - timedelta(days=random.randint(1, 30)),
            )
    
    def create_newsletter_subscriptions(self):
        """Create sample newsletter subscriptions."""
        subscribers = [
            ('subscriber1@example.com', 'Alex Thompson'),
            ('subscriber2@example.com', 'Maria Garcia'),
            ('subscriber3@example.com', 'James Wilson'),
            ('subscriber4@example.com', 'Lisa Chen'),
            ('subscriber5@example.com', 'Michael Davis'),
            ('test@example.com', 'Test User'),
            ('demo@example.com', 'Demo User'),
        ]
        
        for email, name in subscribers:
            Newsletter.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'is_active': True,
                    'preferences': {
                        'frequency': random.choice(['daily', 'weekly', 'monthly']),
                        'topics': random.sample(['django', 'python', 'web-dev'], 2)
                    }
                }
            )
    
    def create_template_examples(self):
        """Create template examples."""
        examples_data = [
            {
                'name': 'Variable Output',
                'description': 'Basic variable output in templates',
                'template_code': '{{ name }} is {{ age }} years old.',
                'demo_data': {'name': 'John', 'age': 30},
                'expected_output': 'John is 30 years old.'
            },
            {
                'name': 'For Loop',
                'description': 'Iterating over a list in templates',
                'template_code': '{% for item in items %}{{ item }}{% if not forloop.last %}, {% endif %}{% endfor %}',
                'demo_data': {'items': ['Apple', 'Banana', 'Cherry']},
                'expected_output': 'Apple, Banana, Cherry'
            },
            {
                'name': 'If Statement',
                'description': 'Conditional rendering in templates',
                'template_code': '{% if user.is_authenticated %}Welcome, {{ user.username }}!{% else %}Please log in.{% endif %}',
                'demo_data': {'user': {'is_authenticated': True, 'username': 'johndoe'}},
                'expected_output': 'Welcome, johndoe!'
            },
            {
                'name': 'Filter Usage',
                'description': 'Using built-in template filters',
                'template_code': '{{ text|upper|truncatewords:3 }}',
                'demo_data': {'text': 'the quick brown fox jumps over the lazy dog'},
                'expected_output': 'THE QUICK BROWN...'
            },
        ]
        
        for data in examples_data:
            TemplateExample.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
