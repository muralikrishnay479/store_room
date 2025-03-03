from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from store import models as store_models
from vendor import models as vendor_models
from django.db import models
from django.db.models.functions import TruncMonth
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from store import models as store_models
from userauths.models import User



from django.http import JsonResponse
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from store import models as store_models


from django.http import JsonResponse
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from store import models as store_models
from userauths.models import User

from django.http import JsonResponse
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from store import models as store_models
from userauths.models import User, Profile

def all_data_for_powerbi(request, user_name=None):
    # If user_name (or email) is provided, filter data for that specific vendor
    if user_name:
        try:
            # Check if user_name is an email or username
            if '@' in user_name:
                user = User.objects.get(email=user_name)
            else:
                user = User.objects.get(username=user_name)

            # Check if the user is a vendor via Profile model
            profile = Profile.objects.get(user=user, user_Type="Vendor")
            vendor = user  # The user object is the vendor

        except (User.DoesNotExist, Profile.DoesNotExist):
            return JsonResponse({"error": "Vendor not found"}, status=404)

        # Fetch products for the specific vendor
        products = store_models.Product.objects.filter(vendor=vendor).values(
            'id', 'name', 'price', 'stock', 'status', 'date'
        )

        # Fetch orders for the specific vendor
        orders = store_models.OrderItem.objects.filter(vendor=vendor).values(
            'order__order_id', 'product__name', 'qty', 'price', 'total', 'date'
        )

        # Fetch monthly sales data for the specific vendor
        monthly_sales = (
            store_models.OrderItem.objects.filter(vendor=vendor)
            .annotate(month=TruncMonth('date'))        
            .values('month')
            .annotate(total_sales=Sum('total'))
            .order_by('-month')
        )

        # Fetch total sales and total products for the specific vendor
        total_sales = store_models.OrderItem.objects.filter(vendor=vendor).aggregate(total_sales=Sum('total'))['total_sales'] or 0
        total_products = store_models.Product.objects.filter(vendor=vendor).count()

    else:
        # If no user_name is provided, fetch all data
        products = store_models.Product.objects.all().values(
            'id', 'name', 'price', 'stock', 'status', 'date', 'vendor__username'
        )

        orders = store_models.OrderItem.objects.all().values(
            'order__order_id', 'product__name', 'qty', 'price', 'total', 'date', 'vendor__username'
        )

        monthly_sales = (
            store_models.OrderItem.objects.annotate(month=TruncMonth('date'))
            .values('month', 'vendor__username')
            .annotate(total_sales=Sum('total'))
            .order_by('-month')
        )

        total_sales = store_models.OrderItem.objects.aggregate(total_sales=Sum('total'))['total_sales'] or 0
        total_products = store_models.Product.objects.count()

    # Fetch all reviews (optional: filter by vendor if needed)
    reviews = store_models.Review.objects.all().values(
        'user__username', 'product__name', 'rating', 'review', 'date'
    )

    # Fetch all coupons (optional: filter by vendor if needed)
    coupons = store_models.Coupon.objects.all().values(
        'vendor__username', 'code', 'discount'
    )

    # Prepare the data to be sent to Power BI
    data = {
        "products": list(products),
        "orders": list(orders),
        "monthly_sales": list(monthly_sales),
        "total_sales": total_sales,
        "total_products": total_products,
        "reviews": list(reviews),
        "coupons": list(coupons),
    }

    return JsonResponse(data)

# Function to get monthly sales data
def get_monthly_sales(user):
    monthly_sales = (
        store_models.OrderItem.objects.filter(vendor=user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=models.Count('id'))
        .order_by('-month')
    )
    return monthly_sales

@login_required
def dashboard(request):
    products = store_models.Product.objects.filter(vendor=request.user)
    orders = store_models.Order.objects.filter(vendors=request.user)
    revenue = store_models.OrderItem.objects.filter(vendor=request.user).aggregate(total=models.Sum(models.F('price') * models.F('qty'), output_field=models.FloatField()))["total"]
    notis = vendor_models.Notifications.objects.filter(user=request.user, seen=False)
    reviews = store_models.Review.objects.filter(product__vendor=request.user)
    rating = store_models.Review.objects.filter(product__vendor=request.user).aggregate(avg=models.Avg('rating'))['avg']
    monthly_sales = get_monthly_sales(request.user)

    context = {
        'products': products,
        'orders': orders,
        'revenue': revenue or 0.00,  # Default to 0.00 if no data
        'notis': notis,
        'reviews': reviews,
        'rating': rating or 0.0,  # Default to 0 if no ratings
        'monthly_sales': monthly_sales,
    }

    return render(request, 'vendor_dashboard.html', context)


# @login_required
# def products(request):
#     products = store_models.Product.objects.filter(vendor=request.user)
#     context = {
#         'products': products
#     }
#     return render(request, 'products.html', context )


from django.core.paginator import Paginator

@login_required
def products(request):
    # Fetch products for the logged-in vendor
    products = store_models.Product.objects.filter(vendor=request.user)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Sorting functionality
    sort_by = request.GET.get('sort_by')
    if sort_by == 'price_low_to_high':
        products = products.order_by('price')
    elif sort_by == 'price_high_to_low':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-average_rating')
    elif sort_by == 'date':
        products = products.order_by('-date')

    # Pagination
    paginator = Paginator(products, 4)  # Show 10 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'products': products,
    }
    return render(request, 'products.html', context)


# @login_required
# def orders(request):
#     orders = store_models.Order.objects.filter(vendors=request.user, payment_status='paid')
#     context = {
#         'orders': orders
#     }
#     return render(request, 'vendor/orders.html', context)



@login_required
def orders(request):
    # Fetch orders where the logged-in user is the vendor
    orders = store_models.Order.objects.filter(vendors=request.user).all()

    # Filter by order status
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(order_status=status_filter)

    # Filter by payment status
    payment_status_filter = request.GET.get('payment_status')
    if payment_status_filter:
        orders = orders.filter(payment_status=payment_status_filter)

    # Calculate vendor-specific totals for each order
    for order in orders:
        order.vendor_total = sum(
            item.price * item.qty for item in order.order_items()
            if item.product.vendor == request.user
        )

    context = {
        'orders': orders,
    }
    return render(request, 'vendor/orders.html', context)
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from store import models as store_models

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from store import models as store_models

@login_required
def order_details(request, order_id):
    # Fetch the order for the logged-in vendor
    order = get_object_or_404(store_models.Order, vendors=request.user, order_id=order_id, payment_status='Paid')
    
    # Calculate vendor-specific totals
    vendor_items = order.order_items().filter(product__vendor=request.user)
    vendor_subtotal = sum(item.price * item.qty for item in vendor_items)
    vendor_shipping = sum(item.shipping for item in vendor_items)
    vendor_tax = sum(item.tax for item in vendor_items)
    vendor_total = vendor_subtotal + vendor_shipping + vendor_tax

    context = {
        'order': order,
        'vendor_items': vendor_items,
        'vendor_subtotal': vendor_subtotal,
        'vendor_shipping': vendor_shipping,
        'vendor_tax': vendor_tax,
        'vendor_total': vendor_total,
    }
    return render(request, 'vendor/order_details.html', context)
@login_required
def order_item_detail(request, order_id, item_id):
    order_item = store_models.OrderItem.objects.get(vendors = request.user, order_id=order_id,payment_status='paid')
    item = store_models.OrderItem.objects.get(item_id=item_id, order=order)
    context = {
        'order_item': order_item,
        item: item
    } 
    
    return render(request,'order_item_detail.html', context)


@login_required
def update_order_status(request,order_id):
    order = store_models.Order.objects.get(vendors=request.user,order_id=order_id, payment_status ='Paid')
    
    if request.method == 'POST':
        order_status = request.POST.get('status')
        order.order_status = order_status
        order.save()
        
        messages.success(request, 'Order status updated successfully')
        return redirect('vendor:order_details', order.order_id)
    return redirect('vendor:order_details', order.order_id)
    

@login_required
def update_order_item_status(request,order_i,item_id):
    order = store_models.Order.objects.get(vendors=request.user,order_id=order_id, payment_status ='Paid')
    item = store_models.OrderItem.objects.get(item_id=item_id, order=order)
   
    if request.method == 'POST':
        order_status = request.POST.get('order_status')
        shipping_service = request.POST.get('shipping_service')
        tracking_id = request.POST.get('tracking_id')
        
        
        item.order_status = order_status
        item.shipping_service = shipping_service
        item.tracking_id = tracking_id
        item.save()
       
        
        messages.success(request, 'item status updated successfully')
        return redirect('vendor:order_item_detail', order.order_id, item.item_id)
    return redirect('vendor:order_item_details', order.order_id)
    


def reports(request):
    return render(request, 'reports.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from store import models as store_models

@login_required
def coupons(request):
    coupons = store_models.Coupon.objects.filter(vendor=request.user)
    context = {
        'coupons': coupons,
    }
    return render(request, 'vendor/coupons.html', context)

@login_required
def update_coupon(request, id):
    coupon = get_object_or_404(store_models.Coupon, vendor=request.user, id=id)
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        discount = request.POST.get('discount')
        coupon.code = code
        coupon.discount = discount
        coupon.save()
        messages.success(request, 'Coupon updated successfully')
        return redirect('vendor:coupons')

@login_required
def create_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        discount = request.POST.get('discount')
        store_models.Coupon.objects.create(vendor=request.user, code=code, discount=discount)
        messages.success(request, 'Coupon created successfully')
        return redirect('vendor:coupons')

@login_required
def delete_coupon(request, id):
    coupon = get_object_or_404(store_models.Coupon, vendor=request.user, id=id)
    coupon.delete()
    messages.success(request, 'Coupon deleted successfully')
    return redirect('vendor:coupons')


@login_required
def reviews(request):
    reviews = store_models.Review.objects.filter(product__vendor=request.user)
    
    # Filter by rating
    rating = request.GET.get('rating')
    if rating:
        reviews = reviews.filter(rating=rating)
    
    # Filter by date
    date = request.GET.get('date')
    if date:
        reviews = reviews.filter(date__date=date)
        
    
    product_name = request.GET.get('product_name')
    if product_name:
        reviews = reviews.filter(product__name__icontains=product_name)

    
    context = {
        'reviews': reviews,
    }
    return render(request, 'vendor/reviews.html', context)

@login_required
def update_replay(request, id):
    review = get_object_or_404(store_models.Review, product__vendor=request.user, id=id)
    if request.method == 'POST':
        reply = request.POST.get('replay')
        review.reply = reply
        review.save()
        messages.success(request, 'Reply updated successfully')
    return redirect('vendor:reviews')

@login_required
def notis(request):
    notis = vendor_models.Notifications.objects.filter(user=request.user).all()
    context = {
        "notis": notis,
    }
    return render(request, "vendor/notis.html", context)

@login_required
def mark_noti_seen(request, id):
    noti = vendor_models.Notifications.objects.get(user=request.user, id=id)
    noti.seen = True
    noti.save()
    
    messages.success(request, "Notification marked as seen")
    return redirect("vendor:notis")  # Fix applied


@login_required 
def profile(request):
    profile = request.user.profile
    
    if request.method == "POST":
        image = request.FILES.get("image")
        full_name = request.POST.get("full_name")
        mobile = request.POST.get("mobile")
        email = request.POST.get("email")
        
        
        if image != None:
            profile.image = image
        profile.full_name = full_name
        profile.mobile = mobile
        
        request.user.save()
        profile.save()
        
        messages.success(request, "Profile updated successfully")
        return redirect("vendor:profile")
    
    context = {"profile": profile}
    return render(request, "vendor/profile.html", context)

@login_required
def change_password(request):
         if request.method == "POST":
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            
            print("Passwords:", current_password, ",",new_password," ,",confirm_password)
            
            if confirm_password != new_password:
                messages.error(request, "New password and confirm password do not match")
                return redirect("vendor:change_password")
            
            if not check_password(current_password, request.user.password):
                messages.error(request, "Current password is incorrect")
                return redirect("vendor:change_password")
            
            request.user.set_password(new_password)
            request.user.save()
            
            messages.success(request, "Password changed successfully")
            return redirect("vendor:change_password")
        
         return render(request, "vendor/change_password.html")
     
     
     


@login_required
def create_product(request):
    
    categories = store_models.Category.objects.all()
    
    if request.method == 'POST':
        # Get form data
        image = request.FILES.get('image')
        name = request.POST.get('name')
        category_id = request.POST.get('category_id')
        price = request.POST.get('price')
        description = request.POST.get('description')
        regular_price = request.POST.get('regular_price')
        shipping = request.POST.get('shipping')
        stock = request.POST.get('stock')
        
        # Create the product
        product = store_models.Product.objects.create(
            vendor=request.user,
            image=image,
            name=name,
            category_id=category_id,
            price=price,
            description=description,
            regular_price=regular_price,
            shipping=shipping,
            stock=stock,
        )
        
        # Redirect to update product page
        return redirect('vendor:update_product',product.id)
    
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/create_product.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from store import models as store_models

@login_required
def update_product(request, id):
    product = get_object_or_404(store_models.Product, vendor=request.user, id=id)
    categories = store_models.Category.objects.all()

    if request.method == 'POST':
        # Get form data
        image = request.FILES.get('image')
        name = request.POST.get('name')
        category_id = request.POST.get('category_id')
        price = request.POST.get('price')
        description = request.POST.get('description')
        regular_price = request.POST.get('regular_price')
        shipping = request.POST.get('shipping')
        stock = request.POST.get('stock')
        category = store_models.Category.objects.get(id=category_id)

        # Update the product
        product.name = name
        product.category = category
        product.price = price
        product.description = description
        product.stock = stock
        product.regular_price = regular_price
        product.shipping = shipping

        if image:
            product.image = image

        product.save()

        # Handle variants and variant items
        variant_ids = request.POST.getlist('variant_id')
        variant_titles = request.POST.getlist('variant_title')

        for i, variant_id in enumerate(variant_ids):
            variant_name = variant_titles[i]

            if variant_id:
                variant = store_models.Variant.objects.filter(id=variant_id, product=product).first()
                if variant:
                    variant.name = variant_name
                    variant.save()
            else:
                variant = store_models.Variant.objects.create(product=product, name=variant_name)

            # Handle variant items
            item_ids = request.POST.getlist(f'item_id_{variant.id}[]')
            item_titles = request.POST.getlist(f'item_title_{variant.id}[]')
            item_descriptions = request.POST.getlist(f'item_description_{variant.id}[]')

            for j in range(len(item_titles)):
                item_id = item_ids[j]
                item_title = item_titles[j]
                item_description = item_descriptions[j]

                if item_id:
                    variant_item = store_models.VariantItem.objects.filter(id=item_id, variant=variant).first()
                    if variant_item:
                        variant_item.title = item_title
                        variant_item.content = item_description
                        variant_item.save()
                else:
                    store_models.VariantItem.objects.create(
                        variant=variant,
                        title=item_title,
                        content=item_description
                    )

        # Handle gallery images
        for file_key, image_file in request.FILES.items():
            if file_key.startswith('image_'):
                store_models.Gallery.objects.create(
                    product=product,
                    image=image_file
                )

        messages.success(request, 'Product updated successfully')
        return redirect('vendor:update_product', product.id)

    context = {
        "product": product,
        "categories": categories,
        "variants": store_models.Variant.objects.filter(product=product),
        "gallery_images": store_models.Gallery.objects.filter(product=product),
    }

    return render(request, 'vendor/update_product.html', context)

@login_required
def delete_variant(request, product_id, variant_id):
    product = get_object_or_404(store_models.Product, id=product_id, vendor=request.user)
    variant = get_object_or_404(store_models.Variant, id=variant_id, product=product)
    variant.delete()
    return JsonResponse({"message": "Variant deleted successfully"})

@login_required
def delete_variant_item(request, product_id, variant_id, item_id):
    variant = get_object_or_404(store_models.Variant, id=variant_id, product_id=product_id)
    item = get_object_or_404(store_models.VariantItem, id=item_id, variant=variant)
    item.delete()
    return JsonResponse({"message": "Variant item deleted successfully"})

@login_required
def delete_gallery_image(request, image_id):
    image = get_object_or_404(store_models.Gallery, id=image_id, product__vendor=request.user)
    image.delete()
    return JsonResponse({"message": "Gallery image deleted successfully"})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(store_models.Product, id=product_id, vendor=request.user)
    product.delete()
    messages.success(request, 'Product deleted successfully')
    return redirect('vendor:products')

def get_product_data(request):
    products = store_models.Product.objects.filter(vendor=request.user).all()
    data = {
        "labels": [product.name for product in products],
        "quantities": [product.stock for product in products],
    }
    return JsonResponse(data)


from django.http import JsonResponse


def get_review_data(request):
    review_counts = {
        "one_star": store_models.Review.objects.filter(rating=1, product__vendor=request.user).count(),
        "two_star": store_models.Review.objects.filter(rating=2, product__vendor=request.user).count(),
        "three_star": store_models.Review.objects.filter(rating=3, product__vendor=request.user).count(),
        "four_star": store_models.Review.objects.filter(rating=4, product__vendor=request.user).count(),
        "five_star": store_models.Review.objects.filter(rating=5, product__vendor=request.user).count(),
    }
    return JsonResponse(review_counts)


from collections import Counter
def get_order_payment_data(request):
    orders = store_models.Order.objects.filter(vendors=request.user).all()

    # Count order statuses
    order_status_counts = dict(Counter(orders.values_list('order_status', flat=True)))

    # Count payment statuses
    payment_status_counts = dict(Counter(orders.values_list('payment_status', flat=True)))

    return JsonResponse({
        "order_status": order_status_counts,
        "payment_status": payment_status_counts
    })
    

from django.db.models import Sum, Count
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Sum
 # Adjust this import based on your actual app structure

def get_sales_data(request):
    try:
        # Daily Sales Data
        daily_sales = (
            store_models.Order.objects.filter(vendors=request.user).all()
            .values('date__year', 'date__month', 'date__day')
            .annotate(total=Sum('total'))
            .order_by('date__year', 'date__month', 'date__day')
        )

        # Monthly Sales Data
        monthly_sales = (
            store_models.Order.objects.filter(vendors=request.user).all()
            .values('date__year', 'date__month')
            .annotate(total=Sum('total'))
            .order_by('date__year', 'date__month')
        )

        # Convert querysets to lists
        daily_sales_list = [{"year": d["date__year"], "month": d["date__month"], "day": d["date__day"], "total": float(d["total"])} for d in daily_sales]
        monthly_sales_list = [{"year": m["date__year"], "month": m["date__month"], "total": float(m["total"])} for m in monthly_sales]

        return JsonResponse({
            "success": True,
            "daily_sales": daily_sales_list,
            "monthly_sales": monthly_sales_list
        }, safe=False)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)