"""
Management command để demo URL patterns và reverse URL
"""
from django.core.management.base import BaseCommand
from django.urls import reverse, resolve
from django.test import Client


class Command(BaseCommand):
    help = 'Demo các URL patterns và reverse URLs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test-urls',
            action='store_true',
            help='Test tất cả URL patterns',
        )
        parser.add_argument(
            '--demo-reverse',
            action='store_true',
            help='Demo reverse URL functionality',
        )
        parser.add_argument(
            '--show-patterns',
            action='store_true',
            help='Hiển thị tất cả URL patterns',
        )
    
    def handle(self, *args, **options):
        if options['test_urls']:
            self.test_urls()
        elif options['demo_reverse']:
            self.demo_reverse()
        elif options['show_patterns']:
            self.show_patterns()
        else:
            self.show_help()
    
    def show_help(self):
        """Hiển thị hướng dẫn sử dụng"""
        self.stdout.write(self.style.SUCCESS('URL Patterns Demo Commands:'))
        self.stdout.write('')
        self.stdout.write('python manage.py demo_urls --test-urls     : Test tất cả URL patterns')
        self.stdout.write('python manage.py demo_urls --demo-reverse  : Demo reverse URL')
        self.stdout.write('python manage.py demo_urls --show-patterns : Hiển thị URL patterns')
        self.stdout.write('')
    
    def test_urls(self):
        """Test tất cả URL patterns"""
        self.stdout.write(self.style.SUCCESS('Testing URL Patterns:'))
        self.stdout.write('')
        
        client = Client()
        
        # Test data
        test_urls = [
            ('/', 'Home page'),
            ('/articles/', 'Articles index'),
            ('/articles/2003/', 'Special case 2003'),
            ('/articles/2024/', 'Year archive'),
            ('/articles/2024/12/', 'Month archive'),
            ('/articles/2024/12/django-urls/', 'Article detail'),
            ('/articles/custom/2024/', 'Custom year converter'),
            ('/articles/re/2024/', 'Regex year pattern'),
            ('/blog/', 'Blog index'),
            ('/blog/page/5/', 'Blog page 5'),
            ('/author-blog/', 'Author blog namespace'),
            ('/publisher-blog/', 'Publisher blog namespace'),
        ]
        
        for url, description in test_urls:
            try:
                response = client.get(url)
                status = '✅ OK' if response.status_code == 200 else f'❌ {response.status_code}'
                self.stdout.write(f'{status} {url:30} - {description}')
            except Exception as e:
                self.stdout.write(f'❌ {url:30} - Error: {e}')
        
        self.stdout.write('')
    
    def demo_reverse(self):
        """Demo reverse URL functionality"""
        self.stdout.write(self.style.SUCCESS('Reverse URL Demo:'))
        self.stdout.write('')
        
        # Basic reverse examples
        reverse_examples = [
            ('articles-index', [], 'Articles index'),
            ('news-year-archive', [2024], 'Year archive'),
            ('news-month-archive', [2024, 12], 'Month archive'),
            ('news-article-detail', [2024, 12, 'django-urls'], 'Article detail'),
            ('blog:index', [], 'Blog index (namespace)'),
            ('author-blog:index', [], 'Author blog (instance namespace)'),
        ]
        
        for name, args, description in reverse_examples:
            try:
                url = reverse(name, args=args)
                self.stdout.write(f'✅ {name:25} -> {url:30} ({description})')
            except Exception as e:
                self.stdout.write(f'❌ {name:25} -> Error: {e}')
        
        self.stdout.write('')
        
        # Resolve examples
        self.stdout.write(self.style.SUCCESS('URL Resolution Demo:'))
        self.stdout.write('')
        
        resolve_examples = [
            '/articles/2024/',
            '/articles/2024/12/',
            '/blog/',
            '/author-blog/',
        ]
        
        for url in resolve_examples:
            try:
                resolver = resolve(url)
                self.stdout.write(f'✅ {url:20} -> {resolver.view_name} {resolver.kwargs}')
            except Exception as e:
                self.stdout.write(f'❌ {url:20} -> Error: {e}')
        
        self.stdout.write('')
    
    def show_patterns(self):
        """Hiển thị tất cả URL patterns"""
        self.stdout.write(self.style.SUCCESS('URL Patterns Overview:'))
        self.stdout.write('')
        
        from django.urls import get_resolver
        from django.conf import settings
        
        urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])
        
        def show_urls(urllist, prefix=''):
            for entry in urllist:
                if hasattr(entry, 'url_patterns'):
                    # Include pattern
                    self.stdout.write(f'{prefix}📁 {entry.pattern}')
                    if hasattr(entry, 'namespace') and entry.namespace:
                        namespace_info = f' (namespace: {entry.namespace})'
                    else:
                        namespace_info = ''
                    if hasattr(entry, 'app_name') and entry.app_name:
                        namespace_info += f' (app: {entry.app_name})'
                    if namespace_info:
                        self.stdout.write(f'{prefix}   {namespace_info}')
                    show_urls(entry.url_patterns, prefix + '  ')
                else:
                    # URL pattern
                    pattern = str(entry.pattern)
                    name = getattr(entry, 'name', 'unnamed')
                    view = entry.callback
                    view_name = f'{view.__module__}.{view.__name__}'
                    self.stdout.write(f'{prefix}🔗 {pattern:30} -> {view_name} (name: {name})')
        
        show_urls(urlconf.urlpatterns)
        self.stdout.write('')
