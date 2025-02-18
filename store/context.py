from store import models as store_models
from customer import models as customer_models
def default(request):
    try:
        cart_id = request.session.get("cart_id")
        total_cart_items = store_models.Cart.objects.filter(cart_id=cart_id).count()
        print("total cart items ",total_cart_items)
    except:
        total_cart_items = 0
    return {
        "total_cart_items": total_cart_items
            }
    
        

