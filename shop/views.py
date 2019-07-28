from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from taggit.models import Tag
from .models import Item

# Create your views here.
def index(request, tag_slug=None):
    item_list = Item.objects.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        item_list = item_list.filter(tags__in=[tag])

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

def product(request, slug):
    item = get_object_or_404(Item, slug=slug)
    item_tags_ids = item.tags.values_list('id', flat=True)
    similar_items = Item.objects.all().filter(tags__in=item_tags_ids).exclude(id=item.id)
    similar_items = similar_items.annotate(same_tags=Count('tags')).order_by('-same_tags')[:3]

    context = {
        'item': item,
        'similar_items': similar_items,
    }
    return render(request, "product-page.html", context)

def checkout(request):
    
    return render(request, "checkout-page.html")