from django.http import HttpResponse
from django.shortcuts import render


def special_case_2003(request):
    """View xử lý trường hợp đặc biệt cho năm 2003"""
    return HttpResponse("Special case for year 2003")


def year_archive(request, year):
    """View hiển thị archive theo năm"""
    return HttpResponse(f"Year archive for {year}")


def month_archive(request, year, month):
    """View hiển thị archive theo năm và tháng"""
    return HttpResponse(f"Month archive for {year}/{month}")


def article_detail(request, year, month, slug):
    """View hiển thị chi tiết bài viết"""
    return HttpResponse(f"Article detail: {slug} from {year}/{month}")


def all_articles(request):
    """View hiển thị tất cả bài viết"""
    return HttpResponse("All articles list")


def latest_articles(request):
    """View hiển thị bài viết mới nhất"""
    return HttpResponse("Latest articles")


def redirect_to_year(request):
    """Ví dụ về reverse URL"""
    from django.http import HttpResponseRedirect
    from django.urls import reverse
    
    year = 2024
    return HttpResponseRedirect(reverse('news-year-archive', args=(year,)))


def url_examples(request):
    """View hiển thị các ví dụ reverse URL"""
    context = {
        'year_list': [2020, 2021, 2022, 2023, 2024]
    }
    return render(request, 'url_examples.html', context)
