from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from . models import Cart, CartItem
from django.http import HttpResponse 
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()   
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # This will get the product
    product_variation = []

    if request.method == "POST":
        for item in request.POST:
            key = item
            value = request.POST[key]
            
            try:
                variation = Variation.objects.get(product = product, variation_category__iexact = key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass    
    

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # Get the cart, using the cart_id present in the session

    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()


    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        # Get the existing variations => get it from the database 
        # and the current varioation => product_variation , which the user selected from the webpage
        # And we need item id aswell , which comes from the database.

        # check if the current variation already availabel in the existing variations
        # then we need to increase the quantity

        ex_var_list = []  # Empty list for all existing variations
        id = []
        for item in cart_item:
            existing_variations = item.variations.all()
            ex_var_list.append(list(existing_variations))
            id.append(item.id)

        print(ex_var_list)

        if product_variation in ex_var_list:
            # Incrase the cart item quantity by one

            idex = ex_var_list.index(product_variation)
            item_id = id[idex]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
            
        else:
            # Here, we need to crate the new item in the cart.
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)

            if len(product_variation) > 0:
                item.variations.clear()
                item.variations.add(*product_variation)
                
            item.save()

    else :
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart,
        )

        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()
        
    return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    except:
        pass

    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    
        for cart_item in cart_items:
            total += (cart_item.product.price * 1.00 * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total) / 100

        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' :cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    #return HttpResponse(CartItem.product)0

    return render(request, 'store/cart.html', context)