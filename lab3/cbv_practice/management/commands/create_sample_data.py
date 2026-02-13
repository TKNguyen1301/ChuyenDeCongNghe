"""
Management command to create sample data for CBV practice
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date
from cbv_practice.models import Author, Category, Book, Article, Comment
import random


class Command(BaseCommand):
    help = 'Create sample data for Class-based Views practice'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data for CBV practice...')
        
        # Clear existing data
        Comment.objects.all().delete()
        Article.objects.all().delete() 
        Book.objects.all().delete()
        Author.objects.all().delete()
        Category.objects.all().delete()
        
        # Create categories
        categories_data = [
            {'name': 'Programming', 'slug': 'programming', 'description': 'Books about programming and software development'},
            {'name': 'Web Development', 'slug': 'web-development', 'description': 'Web technologies and frameworks'},
            {'name': 'Data Science', 'slug': 'data-science', 'description': 'Data analysis, machine learning, and statistics'},
            {'name': 'DevOps', 'slug': 'devops', 'description': 'Development operations and deployment'},
            {'name': 'Mobile Development', 'slug': 'mobile-development', 'description': 'iOS and Android development'},
            {'name': 'Database', 'slug': 'database', 'description': 'Database design and management'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category.objects.create(**cat_data)
            categories.append(category)
            self.stdout.write(f'Created category: {category.name}')
        
        # Create authors
        authors_data = [
            {'name': 'John Smith', 'email': 'john@example.com', 'bio': 'Senior software engineer with 10+ years experience'},
            {'name': 'Jane Doe', 'email': 'jane@example.com', 'bio': 'Full-stack developer and technical writer'},
            {'name': 'Bob Wilson', 'email': 'bob@example.com', 'bio': 'Data scientist and ML engineer'},
            {'name': 'Alice Johnson', 'email': 'alice@example.com', 'bio': 'DevOps engineer and cloud architect'},
            {'name': 'Charlie Brown', 'email': 'charlie@example.com', 'bio': 'Mobile app developer'},
            {'name': 'Diana Prince', 'email': 'diana@example.com', 'bio': 'Database administrator and backend developer'},
            {'name': 'Eve Adams', 'email': 'eve@example.com', 'bio': 'Frontend developer and UX designer'},
            {'name': 'Frank Miller', 'email': 'frank@example.com', 'bio': 'Security specialist and ethical hacker'},
        ]
        
        authors = []
        for author_data in authors_data:
            # Add random birth date
            author_data['birth_date'] = date(
                random.randint(1970, 1990), 
                random.randint(1, 12), 
                random.randint(1, 28)
            )
            author = Author.objects.create(**author_data)
            authors.append(author)
            self.stdout.write(f'Created author: {author.name}')
        
        # Create books
        books_data = [
            {'title': 'Python Programming for Beginners', 'isbn': '9781234567890', 'pages': 350, 'price': 29.99, 'description': 'Learn Python programming from scratch with practical examples.'},
            {'title': 'Advanced Django Web Development', 'isbn': '9781234567891', 'pages': 450, 'price': 39.99, 'description': 'Master Django framework for building robust web applications.'},
            {'title': 'React.js Complete Guide', 'isbn': '9781234567892', 'pages': 520, 'price': 34.99, 'description': 'Comprehensive guide to React.js and modern frontend development.'},
            {'title': 'Machine Learning with Python', 'isbn': '9781234567893', 'pages': 680, 'price': 49.99, 'description': 'Practical machine learning using Python and scikit-learn.'},
            {'title': 'Docker and Kubernetes Mastery', 'isbn': '9781234567894', 'pages': 420, 'price': 44.99, 'description': 'Container orchestration and deployment strategies.'},
            {'title': 'iOS App Development with Swift', 'isbn': '9781234567895', 'pages': 380, 'price': 42.99, 'description': 'Build native iOS applications using Swift programming language.'},
            {'title': 'PostgreSQL Database Administration', 'isbn': '9781234567896', 'pages': 560, 'price': 38.99, 'description': 'Complete guide to PostgreSQL database management.'},
            {'title': 'Vue.js Frontend Framework', 'isbn': '9781234567897', 'pages': 340, 'price': 32.99, 'description': 'Modern frontend development with Vue.js ecosystem.'},
            {'title': 'AWS Cloud Computing', 'isbn': '9781234567898', 'pages': 480, 'price': 46.99, 'description': 'Amazon Web Services cloud infrastructure and services.'},
            {'title': 'Flutter Mobile Development', 'isbn': '9781234567899', 'pages': 400, 'price': 36.99, 'description': 'Cross-platform mobile app development with Flutter.'},
        ]
        
        books = []
        for i, book_data in enumerate(books_data):
            # Random publication date (some recent, some older)
            if i < 3:  # Make first 3 books new releases
                book_data['publication_date'] = timezone.now().date() - timedelta(days=random.randint(1, 25))
            else:
                book_data['publication_date'] = timezone.now().date() - timedelta(days=random.randint(30, 365))
            
            book_data['category'] = random.choice(categories)
            book_data['is_available'] = random.choice([True, True, True, False])  # 75% available
            
            book = Book.objects.create(**book_data)
            
            # Add random authors (1-3 authors per book)
            book_authors = random.sample(authors, random.randint(1, 3))
            book.authors.set(book_authors)
            
            books.append(book)
            self.stdout.write(f'Created book: {book.title}')
        
        # Create articles
        articles_data = [
            {'title': 'Getting Started with Django Class-based Views', 'slug': 'django-class-based-views', 'content': 'Class-based views provide an alternative way to implement views as Python objects instead of functions. This approach offers several advantages including code reusability, inheritance, and better organization of view logic.'},
            {'title': 'Understanding Django ListView', 'slug': 'django-listview', 'content': 'ListView is one of the most commonly used generic class-based views in Django. It provides a convenient way to display a list of objects with built-in pagination, filtering, and context handling.'},
            {'title': 'Mastering Django DetailView', 'slug': 'django-detailview', 'content': 'DetailView displays information about a single object. It automatically handles object retrieval, 404 errors, and context creation, making it perfect for displaying individual items.'},
            {'title': 'Advanced Django Mixins', 'slug': 'django-mixins', 'content': 'Mixins provide a way to reuse common functionality across multiple views. They follow the DRY principle and make your code more maintainable and organized.'},
            {'title': 'Async Views in Django', 'slug': 'django-async-views', 'content': 'Django supports asynchronous views using async/await syntax. This allows for better handling of I/O-bound operations and improved performance in certain scenarios.'},
            {'title': 'Django TemplateView Best Practices', 'slug': 'django-templateview', 'content': 'TemplateView is the simplest class-based view for rendering templates. Learn how to effectively use it for static pages and dynamic content generation.'},
            {'title': 'Form Handling with Class-based Views', 'slug': 'django-form-views', 'content': 'Django provides several form-handling views including FormView, CreateView, UpdateView, and DeleteView. Each serves specific purposes in form processing workflows.'},
            {'title': 'Custom View Mixins Tutorial', 'slug': 'custom-view-mixins', 'content': 'Learn how to create your own mixins to add common functionality like authentication, logging, caching, and more to your class-based views.'},
        ]
        
        articles = []
        for i, article_data in enumerate(articles_data):
            article_data['author'] = random.choice(authors)
            article_data['category'] = random.choice(categories)
            article_data['is_published'] = True
            article_data['published_date'] = timezone.now() - timedelta(days=random.randint(1, 60))
            article_data['views_count'] = random.randint(10, 500)
            
            article = Article.objects.create(**article_data)
            articles.append(article)
            self.stdout.write(f'Created article: {article.title}')
        
        # Create comments
        for article in articles[:5]:  # Add comments to first 5 articles
            for j in range(random.randint(1, 4)):
                Comment.objects.create(
                    article=article,
                    author_name=f'User{j+1}',
                    author_email=f'user{j+1}@example.com',
                    content=f'Great article about {article.title}! Very informative and well-written.',
                    is_approved=random.choice([True, True, False])  # 66% approved
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- {len(categories)} categories\n'
                f'- {len(authors)} authors\n' 
                f'- {len(books)} books\n'
                f'- {len(articles)} articles\n'
                f'- {Comment.objects.count()} comments'
            )
        )
