from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404
from taggit.models import Tag
from .models import Item

# Create your views here.
def item_list(request, tag_slug=None):
    item_list = Item.objects.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        item_list = items.filter(tags__in=[tag])

    paginator = Paginator(item_list, 8)
    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    context = {
        'items': items,
        'tag': tag,
        'page': page
    }
    return render(request, "home-page.html", context)

def product(request):
    
    return render(request, "product-page.html")

def checkout(request):
    
    return render(request, "checkout-page.html")