from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),  # ← ajouté
    path('checkout/', views.checkout, name='checkout'),
    path('contact/', views.contact, name='contact'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('search/', views.search, name='search'),
    path('profile/', views.profile, name='profile'),
  path('wishlist/', views.wishlist, name='wishlist'),
path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
path('remove-from-wishlist/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
path('orders/', views.orders, name='orders'),
path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
path('logout/', views.logout_view, name='logout'),
]
