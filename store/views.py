from django.shortcuts import render
from store import models as store_models



def index(request):
    categories = store_models.Category.objects.all()
    products = store_models.Product.objects.filter(status="Published").order_by('-id')  # Fetch only published products
    return render(request, "index.html", {"categories": categories, "products": products})

def product_detail(request, slug):
    product = store_models.Product.objects.get(status="published", slug=slug)
    related_product= store_models.Product.objects.filter(category=product.category,status="published").exclude(id=product.id)
    context = {
        "product" : product,
        "related_product" : related_product,
    }
    return render(request, "product_detail.html", context)