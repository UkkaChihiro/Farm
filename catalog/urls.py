from django.conf.urls import url

from .views import (add_product_to_favorites, delete_product_from_favorites, show_favorites,
                    add_favorites_list, show_favorites_lists, change_favorites_list, delete_favorites_list,
                    product_list, filter_products)

urlpatterns = [
    url(r'^add_favorite$', add_product_to_favorites, name='add_product_to_favorites'),
    url(r'^delete_favorite$', delete_product_from_favorites, name='delete_product_from_favorites'),
    url(r'^show_favorites$', show_favorites, name='show_favorites'),
    url(r'^add_favorites_list$', add_favorites_list, name='add_favorites_list'),
    url(r'^show_favorites_lists$', show_favorites_lists, name='show_favorites_lists'),
    url(r'^change_favorites_list$', change_favorites_list, name='change_favorites_list'),
    url(r'^delete_favorites_list$', delete_favorites_list, name='delete_favorites_list'),

]
