"""
Database Statistics Management Command
=====================================

This demonstrates a read-only command that generates reports and statistics.
Usage: python manage.py db_stats [--format json|table] [--export FILE]
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Max, Min
from django.utils import timezone
from model_class_practice.models import Article
import json
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Generate database statistics and reports'
    
    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(
            '--format',
            choices=['table', 'json', 'csv'],
            default='table',
            help='Output format (default: table)'
        )
        
        parser.add_argument(
            '--export',
            type=str,
            help='Export results to file'
        )
        
        parser.add_argument(
            '--include-details',
            action='store_true',
            help='Include detailed breakdowns'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Analyze data from last N days (default: 30)'
        )
    
    def handle(self, *args, **options):
        """Main command logic"""
        
        format_type = options['format']
        export_file = options['export']
        include_details = options['include_details']
        days = options['days']
        
        # Generate statistics
        stats = self.generate_statistics(days)
        
        # Format output
        if format_type == 'json':
            output = self.format_json(stats)
        elif format_type == 'csv':
            output = self.format_csv(stats)
        else:
            output = self.format_table(stats, include_details)
        
        # Display or export
        if export_file:
            self.export_to_file(output, export_file, format_type)
            self.stdout.write(
                self.style.SUCCESS(f"Statistics exported to {export_file}")
            )
        else:
            self.stdout.write(output)
    
    def generate_statistics(self, days):
        """Generate comprehensive database statistics"""
        
        # Date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Basic counts
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        superusers = User.objects.filter(is_superuser=True).count()
        
        total_articles = Article.objects.count()
        published_articles = Article.objects.filter(is_published=True).count()
        
        # Recent activity
        recent_articles = Article.objects.filter(
            created__gte=start_date
        ).count()
        
        recent_users = User.objects.filter(
            date_joined__gte=start_date
        ).count()
        
        # Article statistics
        article_stats = Article.objects.aggregate(
            avg_views=Avg('view_count'),
            max_views=Max('view_count'),
            min_views=Min('view_count'),
            total_views=Count('view_count')
        )
        
        # Status breakdown
        status_breakdown = Article.objects.values('status').annotate(
            count=Count('status')
        ).order_by('-count')
        
        # Author statistics
        author_stats = Article.objects.values(
            'author__username'
        ).annotate(
            article_count=Count('id'),
            total_views=Count('view_count')
        ).order_by('-article_count')[:10]
        
        # Monthly trends (last 6 months)
        monthly_trends = []
        for i in range(6):
            month_start = end_date.replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=32)
            month_end = month_end.replace(day=1) - timedelta(days=1)
            
            month_articles = Article.objects.filter(
                created__gte=month_start,
                created__lte=month_end
            ).count()
            
            monthly_trends.insert(0, {
                'month': month_start.strftime('%Y-%m'),
                'articles': month_articles
            })
        
        return {
            'generated_at': end_date.isoformat(),
            'period_days': days,
            'users': {
                'total': total_users,
                'active': active_users,
                'superusers': superusers,
                'recent': recent_users
            },
            'articles': {
                'total': total_articles,
                'published': published_articles,
                'recent': recent_articles,
                'stats': article_stats,
                'status_breakdown': list(status_breakdown),
                'top_authors': list(author_stats),
                'monthly_trends': monthly_trends
            }
        }
    
    def format_table(self, stats, include_details):
        """Format statistics as a readable table"""
        
        output = []
        output.append("=" * 60)
        output.append("DATABASE STATISTICS REPORT")
        output.append("=" * 60)
        output.append(f"Generated: {stats['generated_at']}")
        output.append(f"Period: Last {stats['period_days']} days")
        output.append("")
        
        # Users section
        output.append("USERS")
        output.append("-" * 20)
        users = stats['users']
        output.append(f"Total Users:      {users['total']:,}")
        output.append(f"Active Users:     {users['active']:,}")
        output.append(f"Superusers:       {users['superusers']:,}")
        output.append(f"Recent Signups:   {users['recent']:,}")
        output.append("")
        
        # Articles section
        output.append("ARTICLES")
        output.append("-" * 20)
        articles = stats['articles']
        output.append(f"Total Articles:   {articles['total']:,}")
        output.append(f"Published:        {articles['published']:,}")
        output.append(f"Recent Articles:  {articles['recent']:,}")
        
        if articles['stats']['avg_views']:
            output.append(f"Avg Views:        {articles['stats']['avg_views']:.1f}")
            output.append(f"Max Views:        {articles['stats']['max_views']:,}")
        
        output.append("")
        
        if include_details:
            # Status breakdown
            output.append("ARTICLE STATUS BREAKDOWN")
            output.append("-" * 30)
            for status in articles['status_breakdown']:
                output.append(f"{status['status'].title():15} {status['count']:>5}")
            output.append("")
            
            # Top authors
            output.append("TOP AUTHORS")
            output.append("-" * 20)
            for author in articles['top_authors'][:5]:
                output.append(
                    f"{author['author__username']:15} {author['article_count']:>3} articles"
                )
            output.append("")
            
            # Monthly trends
            output.append("MONTHLY TRENDS")
            output.append("-" * 20)
            for trend in articles['monthly_trends']:
                output.append(f"{trend['month']:10} {trend['articles']:>3} articles")
        
        return "\\n".join(output)
    
    def format_json(self, stats):
        """Format statistics as JSON"""
        return json.dumps(stats, indent=2, default=str)
    
    def format_csv(self, stats):
        """Format statistics as CSV"""
        lines = []
        lines.append("metric,value")
        
        # Basic metrics
        lines.append(f"total_users,{stats['users']['total']}")
        lines.append(f"active_users,{stats['users']['active']}")
        lines.append(f"total_articles,{stats['articles']['total']}")
        lines.append(f"published_articles,{stats['articles']['published']}")
        
        # Add monthly trends
        for trend in stats['articles']['monthly_trends']:
            lines.append(f"articles_{trend['month']},{trend['articles']}")
        
        return "\\n".join(lines)
    
    def export_to_file(self, content, filename, format_type):
        """Export content to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Failed to export to {filename}: {e}")
            )
