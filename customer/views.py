from django.http import JsonResponse
from django.shortcuts import redirect,render
from django.contrib import messages
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password

from store import models as store_models
from customer import models as customer_models
from userauths import models as userauths_models
from django.shortcuts import get_object_or_404 

from plugin.paginate_queryset import paginate_queryset

@login_required
def dashboard(request):
    
    orders=store_models.Order.objects.filter(customer=request.user)
    total_spent=store_models.Order.objects.filter(customer=request.user).aggregate(total=models.Sum("total"))["total"]
    notis = customer_models.Notifications.objects.filter(user=request.user)
	
 
    context={
    "orders":orders,
    "total_spent":total_spent,
    "notis":notis,
    }
    return render(request,"dashboard.html",context)
	
def orders(request):
    orders = store_models.Order.objects.filter(customer=request.user)
    orderlist = paginate_queryset(request, orders, 4)
    context = {
        "orders": orders,
        "orderlist": orderlist,
    }
    return render(request, "orders.html", context)


@login_required
def order_detail(request, order_id):
	order = store_models.Order.objects.get(customer=request.user, order_id=order_id)
	context = {
		"order": order
	}
	return render(request, "order_detail.html", context)


@login_required
def order_items_detail(request, order_id, item_id):
	order = store_models.Order.objects.get(customer=request.user, order_id=order_id)
	item = store_models.OrderItem.objects.get(order=order, item_id=item_id)
	context = {
		"order": order,
		"item":item
	}
	return render(request, "order_item_detail.html", context)




@login_required
def wishlist(request):
    wishlist_list=customer_models.Wishlist.objects.filter(user=request.user)
    wishlist = paginate_queryset(request,wishlist_list, 4)
    context={
        "wishlist_list":wishlist_list,
        "wishlist" : wishlist
    }
    return render(request,"wishlist.html",context)

@login_required
def remove_from_wishlist( request , id):
    print("Removing from wishlist")
    wishlist=customer_models.Wishlist.objects.get(user=request.user,id=id)
    wishlist.delete()
    messages.success(request,"item removed from wishlist")
    return redirect("customer:wishlist")




@login_required
def add_to_wishlist(request, id):
    if request.user.is_authenticated:
        # Use get_object_or_404 to fetch the product or return a 404 error if not found
        product = get_object_or_404(store_models.Product, id=id)

        # Check if the product is already in the user's wishlist
        wishlist_exists = customer_models.Wishlist.objects.filter(product=product, user=request.user).first()
        if not wishlist_exists:
            # Add the product to the wishlist if it doesn't already exist
            customer_models.Wishlist.objects.create(user=request.user, product=product)

        # Get the updated wishlist count for the user
        wishlist = customer_models.Wishlist.objects.filter(user=request.user)
        return JsonResponse({
            "message": "Item added to wishlist",
            "wishlist_count": wishlist.count()
        })
    else:
        return JsonResponse({
            "message": "User is not logged in",
            "wishlist_count": 0
        })
        


@login_required
def notis(request):
    notis = customer_models.Notifications.objects.filter(user=request.user, seen=False)
    context = {
        "notis": notis,
    }
    return render(request, "notis.html", context)


@login_required
def mark_noti_seen(request, id):
    noti = customer_models.Notifications.objects.get(user=request.user, id=id)
    noti.seen = True
    noti.save()
    
    messages.success(request, "Notification marked as seen")
    return redirect("customer:notis")




@login_required
def addresses(request):
    addresses = customer_models.Address.objects.filter(user=request.user)
    context = {
        "addresses": addresses
    }
    
    return render(request, "addresses.html", context)

@login_required
def address_detail(request, id):
    address = customer_models.Address.objects.get(user=request.user, id=id)
    
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        mobile = request.POST.get("mobile")
        email = request.POST.get("email")
        country = request.POST.get("country")
        state = request.POST.get("state")
        city = request.POST.get("city")
        address_location = request.POST.get("address_location")
        zip_code = request.POST.get("zip_code")
        
        address.full_name = full_name
        address.mobile = mobile
        address.email = email
        address.country = country
        address.state = state
        address.city = city
        address.addresse = address_location
        address.zip_code = zip_code
        address.save()
        
        messages.success(request, "Address updated successfully")
        return redirect("customer:addresses")
    
    context = {"address": address}
    return render(request, "address_detail.html", context)


def address_detail(request, id):
    address = get_object_or_404(customer_models.Address, user=request.user, id=id)

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        mobile = request.POST.get("mobile")
        email = request.POST.get("email")
        country = request.POST.get("country")
        state = request.POST.get("state")
        city = request.POST.get("city")
        address_location = request.POST.get("address_location")
        zip_code = request.POST.get("zip_code")

        address.full_name = full_name
        address.mobile = mobile
        address.email = email
        address.country = country
        address.state = state
        address.city = city
        address.addresse = address_location
        address.zip_code = zip_code
        address.save()

        messages.success(request, "Address updated successfully")
        return redirect("customer:addresses")  

  
    context = {"address": address}
    return render(request, "address_detail.html", context)


@login_required
def address_create(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        mobile = request.POST.get("mobile")
        email = request.POST.get("email")
        country = request.POST.get("country")
        state = request.POST.get("state")
        city = request.POST.get("city")
        address_location = request.POST.get("address_location")
        zip_code = request.POST.get("zip_code")
        
        
        customer_models.Address.objects.create(
            user = request.user,
            full_name = full_name,
            mobile = mobile,
            email = email,
            country = country,
            state = state,
            city = city,
            address = address_location,
            zip_code = zip_code,
        )
        
        messages.success(request, "Address created successfully")
        return redirect("customer:addresses")
    
    return render(request, "address_create.html")


@login_required
def delete_address(request,id):
    address = customer_models.Address.objects.get(user=request.user, id=id)
    address.delete()
    
    messages.success(request, "Address deleted successfully")
    return redirect("customer:addresses")


@login_required 
def profile(request):
    profile = request.user.Profile
    
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
        return redirect("customer:profile")
    
    context = {"profile": profile}
    return render(request, "profile.html", context)

@login_required
def change_password(request):
         if request.method == "POST":
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            
            print("Passwords:", current_password, ",",new_password," ,",confirm_password)
            
            if confirm_password != new_password:
                messages.error(request, "New password and confirm password do not match")
                return redirect("customer:change_password")
            
            if not check_password(current_password, request.user.password):
                messages.error(request, "Current password is incorrect")
                return redirect("customer:change_password")
            
            request.user.set_password(new_password)
            request.user.save()
            
            messages.success(request, "Password changed successfully")
            return redirect("customer:change_password")
        
         return render(request, "change_password.html")