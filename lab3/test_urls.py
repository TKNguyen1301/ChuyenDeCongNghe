"""
Test file để kiểm tra tất cả URL patterns
"""
from django.test import TestCase
from django.urls import reverse, resolve
from django.http import HttpResponse


class URLPatternsTest(TestCase):
    """Test các URL patterns trong project"""
    
    def test_articles_basic_urls(self):
        """Test basic URL patterns trong articles app"""
        # Test articles index
        url = reverse('articles-index')
        self.assertEqual(url, '/articles/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test special case 2003
        url = reverse('special-2003')
        self.assertEqual(url, '/articles/2003/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test year archive
        url = reverse('news-year-archive', args=[2024])
        self.assertEqual(url, '/articles/2024/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test month archive
        url = reverse('news-month-archive', args=[2024, 12])
        self.assertEqual(url, '/articles/2024/12/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test article detail
        url = reverse('news-article-detail', args=[2024, 12, 'django-urls'])
        self.assertEqual(url, '/articles/2024/12/django-urls/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_custom_converters(self):
        """Test custom path converters"""
        # Test custom year converter
        url = reverse('custom-year-archive', args=[2024])
        self.assertEqual(url, '/articles/custom/2024/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test custom month converter
        url = reverse('custom-month-archive', args=[2024, 12])
        self.assertEqual(url, '/articles/custom/2024/12/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_regex_patterns(self):
        """Test regex patterns"""
        url = reverse('re-year-archive', args=[2024])
        self.assertEqual(url, '/articles/re/2024/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_blog_namespaces(self):
        """Test blog namespaces"""
        # Test basic blog namespace
        url = reverse('blog:index')
        self.assertEqual(url, '/blog/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test instance namespaces
        url = reverse('author-blog:index')
        self.assertEqual(url, '/author-blog/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        url = reverse('publisher-blog:index')
        self.assertEqual(url, '/publisher-blog/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_url_resolution(self):
        """Test URL resolution"""
        # Test resolve function
        resolver = resolve('/articles/2024/')
        self.assertEqual(resolver.view_name, 'news-year-archive')
        self.assertEqual(resolver.kwargs, {'year': 2024})
        
        resolver = resolve('/blog/')
        self.assertEqual(resolver.view_name, 'blog:index')
        
    def test_url_ordering(self):
        """Test URL pattern ordering"""
        # 2003 should match special case, not year archive
        resolver = resolve('/articles/2003/')
        self.assertEqual(resolver.view_name, 'special-2003')
        
    def test_redirect_view(self):
        """Test redirect view"""
        response = self.client.get('/articles/redirect/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/articles/2024/')


class ConverterTest(TestCase):
    """Test custom converters"""
    
    def test_four_digit_year_converter(self):
        """Test FourDigitYearConverter"""
        from articles.converters import FourDigitYearConverter
        
        converter = FourDigitYearConverter()
        
        # Test valid years
        self.assertEqual(converter.to_python('2024'), 2024)
        self.assertEqual(converter.to_url(2024), '2024')
        
        # Test regex - sử dụng fullmatch để match toàn bộ string
        import re
        pattern = re.compile('^' + converter.regex + '$')
        self.assertTrue(pattern.match('2024'))
        self.assertFalse(pattern.match('24'))  # Too short
        self.assertFalse(pattern.match('12345'))  # Too long
    
    def test_month_converter(self):
        """Test MonthConverter"""
        from articles.converters import MonthConverter
        
        converter = MonthConverter()
        
        # Test valid months
        self.assertEqual(converter.to_python('01'), 1)
        self.assertEqual(converter.to_python('12'), 12)
        self.assertEqual(converter.to_url(1), '01')
        self.assertEqual(converter.to_url(12), '12')
        
        # Test regex
        import re
        pattern = re.compile(converter.regex)
        self.assertTrue(pattern.match('01'))
        self.assertTrue(pattern.match('12'))
        self.assertFalse(pattern.match('00'))  # Invalid
        self.assertFalse(pattern.match('13'))  # Invalid
