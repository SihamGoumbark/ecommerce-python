from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Product, Order, Category, Wishlist


class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse Email")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


# Page d'accueil
def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    services = [
        {'icon': 'truck', 'title': 'Livraison rapide', 'text': 'Recevez vos produits rapidement avec suivi en temps réel.'},
        {'icon': 'lock', 'title': 'Paiement sécurisé', 'text': 'Paiement simple et sûr via cartes bancaires ou à la livraison.'},
        {'icon': 'headset', 'title': 'Support client', 'text': 'Une équipe réactive disponible pour toutes vos questions.'}
    ]
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
        'services': services
    })


# Afficher le shop
def shop(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    return render(request, 'store/shop.html', {
        'products': products,
        'search_query': query
    })


# Page du panier
def cart(request):
    cart_items = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart_items.keys())
    cart_details = []
    total = 0
    for product in products:
        quantity = cart_items[str(product.id)]
        subtotal = product.price * quantity
        total += subtotal
        cart_details.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
    return render(request, 'store/cart.html', {'cart_details': cart_details, 'total': total})


# Ajouter au panier
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    messages.success(request, "Produit ajouté au panier avec succès !")
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# Supprimer du panier
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
    return redirect('cart')


# Page de checkout
@login_required
def checkout(request):
    cart_items = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart_items.keys())

    total = 0
    for product in products:
        total += product.price * cart_items[str(product.id)]

    if request.method == 'POST':
        Order.objects.create(
            user=request.user,
            total_price=total,
            city="Non renseignée",
            delivery_fee=10
        )
        request.session['cart'] = {}
        messages.success(request, "Commande validée avec succès !")
        return redirect('orders')

    return render(request, 'store/checkout.html', {'total': total})

def contact(request):
    return render(request, 'store/contact.html')


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()
    return render(request, 'store/category.html', {
        'category': category,
        'products': products
    })


def search(request):
    query = request.GET.get('q')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    return render(request, 'store/shop.html', {
        'products': products,
        'search_query': query
    })


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'items': items})


def add_to_wishlist(request, product_id):
    if request.user.is_authenticated:
        product = Product.objects.get(id=product_id)
        Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('wishlist')


@login_required
def remove_from_wishlist(request, item_id):
    Wishlist.objects.filter(id=item_id, user=request.user).delete()
    return redirect('wishlist')


@login_required
def profile(request):
    if request.method == 'POST':
        new_username = request.POST.get('username', '').strip()
        new_email = request.POST.get('email', '').strip()
        if new_username:
            request.user.username = new_username
        request.user.email = new_email
        request.user.save()
        messages.success(request, "Profil mis à jour avec succès !")
        return redirect('profile')

    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/profile.html', {
        'user': request.user,
        'orders': user_orders
    })


@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/orders.html', {'orders': user_orders})
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Bienvenue {user.username} ! Connexion réussie.")
            return redirect('profile')
    else:
        form = AuthenticationForm()
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    return render(request, 'store/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            auth_login(request, user)
            messages.success(request, f"Bienvenue {user.username} ! Votre compte a été créé.")
            return redirect('profile')
    else:
        form = CustomRegisterForm()
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    return render(request, 'store/register.html', {'form': form})
def logout_view(request):
    auth_logout(request)
    messages.success(request, "Vous êtes déconnecté.")
    return redirect('login')