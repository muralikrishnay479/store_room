from django.shortcuts import render
from store import models as store_models
from django.http import JsonResponse
from decimal import Decimal
from django.db.models import Q, Avg, Sum
from customer import models as customer_models
from django.contrib import messages
from django.shortcuts import redirect
from plugin.tax_calculation import calculate_tax as tax_calculation
from plugin.service_fee import calculate_service_fee
from django.conf import settings
import requests
from django.core.mail import EmailMultiAlternatives

from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt

import razorpay

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET)) 



def index(request):
    categories = store_models.Category.objects.all()
    products = store_models.Product.objects.filter(status="Published").order_by('-id')  # Fetch only published products
    return render(request, "index.html", {"categories": categories, "products": products})

def product_detail(request, slug):
    product = store_models.Product.objects.get(status="published", slug=slug)
    related_product= store_models.Product.objects.filter(category=product.category,status="published").exclude(id=product.id)
    product_stock_range = range(1, product.stock + 1)
    context = {
        "product" : product,
        "related_product" : related_product,
    }
    return render(request, "product_detail.html", context)

def add_to_cart(request):
    id = request.GET.get("id")
    quantity = request.GET.get("quantity")
    color = request.GET.get("color", "")
    size = request.GET.get("size", "")
    cart_id = request.GET.get("cart_id")  # Get from request first

    # If cart_id is not in session, store it
    # if not request.session.get("cart_id"):
    request.session["cart_id"] = cart_id

    # Use session-stored cart_id
    # cart_id = request.session.get("cart_id")
    

    print(f"id: {id}, quantity: {quantity}, color: {color}, size: {size}, cart_id: {cart_id}")


    if not id or not quantity or not cart_id: 
        return JsonResponse({"error": "No id or quantity or cart_id"}, status=400)
    
    
    try:
        product = store_models.Product.objects.get(status="published", id=id)
    except store_models.Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=400)


    existing_cart_items = store_models.Cart.objects.filter(cart_id=cart_id, product=product,).first()
    if(int(quantity) > product.stock):
        return JsonResponse({"error": "quantity exceeded current stock"}, status=400)

    if not existing_cart_items:
        cart = store_models.Cart()
        cart.product = product
        cart.qty = quantity
        cart.color = color
        cart.size = size
        cart.price = product.price
        cart.sub_total = Decimal(product.price) * Decimal(quantity)
        cart.shipping = Decimal(product.shipping) * Decimal(quantity)
        cart.total = cart.sub_total + cart.shipping
        cart.user = request.user if request.user.is_authenticated else None
        cart.cart_id = cart_id

        message = "Product added to cart"
        cart.save()
    else:
        existing_cart_items.product = product
        existing_cart_items.quantity = quantity
        existing_cart_items.color = color
        existing_cart_items.size = size
        existing_cart_items.price = product.price
        existing_cart_items.sub_total = Decimal(product.price) * Decimal(quantity)
        existing_cart_items.shipping = Decimal(product.shipping) * Decimal(quantity)
        existing_cart_items.total = existing_cart_items.sub_total + existing_cart_items.shipping
        existing_cart_items.user = request.user if request.user.is_authenticated else None
        existing_cart_items.cart_id = cart_id
        existing_cart_items.save()

        message = "Product updated in cart"

    total_cart_items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(cart_id=cart_id))
    cart_sub_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(sub_total=Sum('sub_total'))['sub_total']

    return JsonResponse({
        "message": message,
        "total_cart_items": total_cart_items.count(),
        "cart_sub_total": "{:,.2f}".format(cart_sub_total),
        "item_sub_total": "{:,.2f}".format(existing_cart_items.sub_total) if existing_cart_items else "{:,.2f}".format(cart.sub_total)
    }, status=200)




@login_required
def cart(request):
    if "cart_id" in request.session:
        cart_id = request.session.get("cart_id")
    else:
        cart_id = None
        
    items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | (Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id)))
    cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | (Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id))).aggregate(sub_total=Sum('sub_total'))["sub_total"]
    try:
        addresses = customer_models.Address.objects.filter(user=request.user)
    except:
        addresses = None
        
        messages.warning(request, "No items in cart")
        messages.warning(request, "No items in cart")
        return redirect("store:index")   
    
    context={
        "items": items,
        "addresses": addresses,
        "cart_sub_total": cart_sub_total, 
    }
    
    return render(request, "cart.html", context)

def delete_cart_item(request):
    item_id = request.GET.get("item_id")
    cart_id = request.GET.get("cart_id")
    
    if not item_id or not cart_id:
        return JsonResponse({"error": "No item_id or cart_id"}, status=400)
    
    try:
        item = store_models.Cart.objects.get(id=item_id, cart_id=cart_id)
    except store_models.Cart.DoesNotExist:
        return JsonResponse({"error": "Cart item not found"}, status=404)
    
    item.delete()
    
    cart_sub_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(sub_total=Sum('sub_total'))["sub_total"]
    
    return JsonResponse({
        "message": "Item deleted from cart",
        "total_cart_items": store_models.Cart.objects.filter(cart_id=cart_id).count(),
        "cart_sub_total": "{:,.2f}".format(cart_sub_total) if cart_sub_total else 0.00
    }, status=200)
    
def create_order(request):
    if request.method == "POST":
        address_id = request.POST.get("address")
    print(f"address_id: {address_id}")    
    if not address_id:
        messages.warning(request, "Please select an address")
        return redirect("store:cart")
        
        
    address = customer_models.Address.objects.filter(user=request.user, id=address_id).first()  

    if 'cart_id' in request.session:
        cart_id = request.session.get('cart_id')
    else:
        cart_id = None
        
    items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | (Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id)))
    cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | (Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id))).aggregate(sub_total=Sum('sub_total'))["sub_total"]
    cart_shipping_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | (Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id))).aggregate(shipping=Sum('shipping'))["shipping"]
    
    order = store_models.Order()
    order.sub_total = cart_sub_total
    order.customer = request.user # if request.user.is_authenticated else None
    order.shipping = cart_shipping_total
    order.tax = tax_calculation(address.country, cart_sub_total)
    order.total = order.sub_total + order.shipping + Decimal(order.tax)
    order.service_fee = calculate_service_fee(order.total)
    order.total += order.service_fee
    order.address = address
    order.initial_total = order.total
    order.save()
    
    for i in items:
        store_models.OrderItem.objects.create(
            order=order,
            product=i.product,
            qty=i.qty,
            color=i.color,
            size=i.size,
            price=i.price,
            sub_total=i.sub_total,
            shipping=i.shipping,
            tax=tax_calculation(address.country, i.sub_total),
            total=i.total,
            initial_total=i.total,
            vendor=i.product.vendor,
        )
        
        order.vendors.add(i.product.vendor)
        
    return redirect("store:checkout", order.order_id)  

from django.shortcuts import render, get_object_or_404
from django.conf import settings
import razorpay
from . import models as store_models

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def checkout(request, order_id):
    order = get_object_or_404(store_models.Order, order_id=order_id)
    amount_in_inr = int(order.total * 100)  # Convert to paise
    print("Checking out:", order_id, order.total, amount_in_inr)
    print('Initialized Razorpay client', settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    try:
        razorpay_order = razorpay_client.order.create({
            "amount": amount_in_inr,
            "currency": "INR",
            "payment_capture": 1,
        })
    except Exception as e:
        print(f"Error creating Razorpay order: {e}")
        razorpay_order = None

    context = {
        "order": order,
        "paypal_client_id" : settings.PAYPAL_CLIENT_ID,
        "RAZORPAY_KEY_ID": settings.RAZORPAY_KEY_ID,
        "amount_in_inr": amount_in_inr,
        "razorpay_order_id": razorpay_order["id"] if razorpay_order else None,
    }
    return render(request, "checkout.html", context)
def coupon_apply(request, order_id):
    try:
        order = store_models.Order.objects.get(order_id=order_id)
        order_items = store_models.OrderItem.objects.filter(order=order)
    except store_models.Order.DoesNotExist:
        return redirect("store:cart")
    
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        
        if not coupon_code:
            messages.error(request, "Please enter a coupon code")
            return redirect("store:checkout", order.order_id)
        
        try:
            coupon = store_models.Coupon.objects.get(code=coupon_code)
        except store_models.Coupon.DoesNotExist:
            messages.error(request, "Coupon not found")
            return redirect("store:checkout", order.order_id)
        
        if coupon in order.coupons.all():
            messages.error(request, "Coupon already applied")
            return redirect("store:checkout", order.order_id)
        else:
            total_discount = 0
            
            
            for item in order_items:
                if coupon.vendor == item.product.vendor and coupon not in item.coupons.all():
                    item_discount = item.total * coupon.discount / 100
                    total_discount += item_discount
                    
                    item.coupons.add(coupon)
                    item.total -= item_discount
                    item.saved += item_discount
                    item.save()
                    
            if total_discount > 0:
                order.coupons.add(coupon)
                order.total -= total_discount
                order.sub_total -= total_discount
                order.save()
                                
        messages.success(request, "Coupon applied successfully")
        return redirect("store:checkout", order.order_id)
                    
def clear_cart_items(request):
    try:
        cart_id = request.session.get("cart_id")
        store_models.Cart.objects.filter(cart_id=cart_id).delete()
    except Exception as e:
        print(f"Error clearing cart items: {e}")
    return   
    
    
def get_paypal_access_token():
    url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    data = {
        "grant_type": "client_credentials"
    }
    auth = (settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET_ID)
    
    response = requests.post(url, data=data, auth=auth)
    
    if response.status_code == 200:
        return response.json()["access_token"]  
    else:
        raise Exception(f"Failed to get access token from PayPal: {response.status_code}")
    
    
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

def paypal_payment_verify(request, order_id):
    order = get_object_or_404(store_models.Order, order_id=order_id)
    
    transaction_id = request.GET.get("transaction_id")
    paypal_api_url = f"https://api.sandbox.paypal.com/v2/checkout/orders/{transaction_id}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_paypal_access_token()}"  
    }
    
    response = requests.get(paypal_api_url, headers=headers)
    
    if response.status_code == 200:
        paypal_order_data = response.json()
        paypal_payment_status = paypal_order_data["status"]
        payment_method = "PayPal"
        
        if paypal_payment_status == "COMPLETED":
            order.status = "Paid"
            order.payment_status = "Paid"
            order.payment_method = payment_method
            order.save()
            clear_cart_items(request)
            
            customer_merge_data = {
                'order' : order,
                'order_items' : order.order_items(),
            }
            
            subject = f"New Order"
            text_body = render_to_string("email/order/customer/customer_new_order.txt", customer_merge_data)
            html_body = render_to_string("email/order/customer/customer_new_order.html", customer_merge_data)
            msg = EmailMultiAlternatives(
                subject = subject,
                from_email = settings.FROM_EMAIL,
                to = [order.address.email], 
                # to = [order.address.email], 
                body= text_body,
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send()
            
            customer_models.Notifications.objects.create(
                    type="New Order",
                    user=request.user,
                )
            
            for item in order.order_items():
                vendor_merge_data = {
                    'item' : item,
                }
                
                subject = f"New Order"
                text_body = render_to_string("email/order/vendor/vendor_new_order.txt", vendor_merge_data)
                html_body = render_to_string("email/order/vendor/vendor_new_order.html", vendor_merge_data)
                
                msg = EmailMultiAlternatives(
                    subject = subject,
                    from_email = settings.FROM_EMAIL,
                    to = [item.vendor.email], 
                    body= text_body,
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send()
                
                vendor_models.Notifications.objects.create(
                    type="New Order",
                    user=request.user,
                    order=item,
                )
                
                
            # Use reverse to construct the correct URL
            return redirect(reverse('store:payment_status', args=[order.order_id]) + f"?payment_status=paid")
        else:
            return redirect(reverse('store:payment_status', args=[order.order_id]) + f"?payment_status=failed")
    else:
        return redirect(reverse('store:payment_status', args=[order.order_id]) + f"?payment_status=failed")   
    
def payment_status(request, order_id):
    order = get_object_or_404(store_models.Order, order_id=order_id)
    payment_status = request.GET.get("payment_status", None)

    context = {
        "order": order,
        "payment_status": payment_status,
        "paypal_client_id": settings.PAYPAL_CLIENT_ID,
    }
    return render(request, "payment_status.html", context)





from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import razorpay
from . import models as store_models
from django.template.loader import render_to_string
from vendor import models as vendor_models

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def razorpay_payment_verify(request, order_id):
    order = get_object_or_404(store_models.Order, order_id=order_id)
    payment_method = request.GET.get("payment_method")

    if request.method == "POST":
        data = request.POST

        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")
        
        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        try:
            # Verify payment signature
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Update order status
            if order.payment_status == "Processing":
                order.payment_status = "Paid"
                order.payment_method = payment_method
                order.save()
                clear_cart_items(request)
                return redirect(reverse('store:payment_status', args=[order.order_id]) + "?payment_status=paid")
            else:
                return redirect(reverse('store:payment_status', args=[order.order_id]) + "?payment_status=failed")
        except razorpay.errors.SignatureVerificationError as e:
            print(f"Razorpay signature verification failed: {e}")
            return redirect(reverse('store:payment_status', args=[order.order_id]) + "?payment_status=failed")
        except Exception as e:
            print(f"Error during payment verification: {e}")
            return redirect(reverse('store:payment_status', args=[order.order_id]) + "?payment_status=failed")

    return redirect(reverse('store:payment_status', args=[order.order_id]) + "?payment_status=failed")