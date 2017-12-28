from django.conf.urls import url

from geodata.views import get_country, get_region, get_city

from delivery.views import (
    add_tariff_for_country, get_tariff_for_country, delete_tariff_for_country,
    add_tariff_for_group, get_tariff_for_group,
    get_group_of_countries,
    add_tariff_for_product, get_tariff_for_product
)

from core.views import *

from userdata.views import *

from orders.views import (
    get_cart, add_product_to_cart, update_count_of_products_in_cart,
    delete_product_from_cart, get_my_carts, checkout,
    update_order_status, get_my_orders, get_my_sales,
    get_order_status_history
)

from catalog.views import *

from farm.views import (
    add_farm, update_farm, delete_farm, get_all_my_farms, get_farm, get_farm_list
)


urlpatterns = [
    url(r'^check_auth/', check_auth, name='check_auth'),
    url(r'^sign_in/$',sign_in, name='sign_in'),
    url(r'^sign_out/$', sign_out, name='sign_out'),
    url(r'^logout_from_all_devices/$', logout_from_all_devices, name='logout_from_all_devices'),
    url(r'^change_profile/$', change_profile, name='change_profile'),
    url(r'^create_account/$', create_account, name='create_account'),
    url(r'^gen_email_confirmation/$', gen_email_confirmation, name='gen_email_confirmation'),
    url(r'^confirm_email/$', confirm_email, name='confirm_email'),
    url(r'^gen_email_reset_password/$', gen_email_reset_password, name='gen_email_reset_password'),
    url(r'^reset_password/$', reset_password, name='reset_password'),

    url(r'^get_country_groups/$', get_country_groups, name='get_country_groups'),
    url(r'^get_countries/$', get_countries, name='get_countries'),
    url(r'^get_regions/$', get_regions, name='get_regions'),
    url(r'^get_cities/$', get_cities, name='get_cities'),
    url(r'^get_country_num_code/$', get_country_num_code, name='get_country_num_code'),

    url(r'^autocomplete_country/$', autocomplete_country, name='autocomplete_country'),
    url(r'^autocomplete_region/$', autocomplete_region, name='autocomplete_region'),
    url(r'^autocomplete_city/$', autocomplete_city, name='autocomplete_city'),

    url(r'^change_password/$', change_password, name='change_password'),
    url(r'^set_numberphone/$', set_numberphone, name='set_numberphone'),
    url(r'^get_personal_notifications/$', get_personal_notifications, name='get_personal_notifications'),
    url(r'^set_personal_notifications/$', set_personal_notifications, name='set_personal_notifications'),
    url(r'^get_personal_address_book/$', get_personal_address_book, name='get_personal_address_book'),
    url(r'^delete_address/$', delete_address, name='delete_address'),
    url(r'^add_address/$', add_address, name='add_address'),
    url(r'^change_address/$', change_address, name='change_address'),
    url(r'^mark_address_as_default/$', mark_address_as_default, name='mark_address_as_default'),

    url(r'^dashboard_personal/$', dashboard_personal, name='dashboard_personal'),
    url(r'^update_personal_profile/$', update_personal_profile, name='update_personal_profile'),
    url(r'^get_personal_settings/$', get_personal_settings, name='get_personal_settings'),
    url(r'^update_personal_language/$', update_personal_language, name='update_personal_language'),
    url(r'^update_personal_avatar/$', update_personal_avatar, name='update_personal_avatar'),
    url(r'^update_profile_global_filter/$', update_profile_global_filter, name='update_profile_global_filter'),

    url(r'^add_farm/$', add_farm, name='add_farm'),
    url(r'^update_farm/$', update_farm, name='update_farm'),
    url(r'^delete_farm/$', delete_farm, name='delete_farm'),
    url(r'^get_all_my_farms/$', get_all_my_farms, name='get_all_my_farms'),
    url(r'^get_farm/$', get_farm, name='get_farm'),

    url(r'^get_business_address_book/$', get_business_address_book, name='get_business_address_book'),

    url(r'^add_product_to_cart/$', add_product_to_cart, name='add_product_to_cart'),
    url(r'^update_count_of_products_in_cart/$', update_count_of_products_in_cart, name='update_count_of_products_in_cart'),
    url(r'^delete_product_from_cart/$', delete_product_from_cart, name='delete_product_from_cart'),
    url(r'^get_my_carts/$', get_my_carts, name='get_my_carts'),
    url(r'^get_cart/$', get_cart, name='get_cart'),
    url(r'^checkout/$', checkout, name='checkout'),
    url(r'^update_order_status/$', update_order_status, name='update_order_status'),
    url(r'^get_my_orders/$', get_my_orders, name='get_my_orders'),
    url(r'^get_my_sales/$', get_my_sales, name='get_my_sales'),
    url(r'^get_order_status_history/$', get_order_status_history, name='get_order_status_history'),

    url(r'^add_product_by_seller_step_one/$', add_product_by_seller_step_one, name='add_product_by_seller_step_one'),
    url(r'^delete_product/$', delete_product, name='delete_product'),
    url(r'^delete_products/$', delete_products, name='delete_products'),
    url(r'^get_product/$', get_product, name='get_product'),
    url(r'^farmer_product_list/$', farmer_product_list, name='farmer_product_list'),
    url(r'^update_product_by_seller/$', update_product_by_seller, name='update_product_by_seller'),
    url(r'^get_my_products', get_my_products, name='get_my_products'),
    url(r'^find_product_by_name_for_seller', find_product_by_name_for_seller, name='find_product_by_name_for_seller'),

    url(r'^send_msg_reset_password/$', send_msg_reset_password, name='send_msg_reset_password'),

    url(r'^dashboard_business/$', dashboard_business, name='dashboard_business'),
    url(r'^upgrade_profile_to_business/$', upgrade_profile_to_business, name='upgrade_profile_to_business'),
    url(r'^get_form_update_business_profile/$', get_form_update_business_profile, name='get_form_update_business_profile'),
    url(r'^update_business_profile/$', update_business_profile, name='update_business_profile'),

    url(r'^get_business_legal_address/$', get_business_legal_address, name='get_business_legal_address'),

    url(r'^update_business_avatar/$', update_business_avatar, name='update_business_avatar'),

    url(r'^get_city/$', get_city, name='get_city'),
    url(r'^get_country/$', get_country, name='get_country'),
    url(r'^get_region/$', get_region, name='get_region'),

    url(r'^add_tariff_for_country/$', add_tariff_for_country, name='add_tariff_for_country'),
    url(r'^add_tariff_for_group/$', add_tariff_for_group, name='add_tariff_for_group'),
    url(r'^delete_tariff_for_country/$', delete_tariff_for_country, name='delete_tariff_for_country'),
    url(r'^get_tariff_for_country/$', get_tariff_for_country, name='get_tariff_for_country'),
    url(r'^get_tariff_for_group/$', get_tariff_for_group, name='get_tariff_for_group'),
    url(r'^get_group_of_countries/$', get_group_of_countries, name='get_group_of_countries'),
    url(r'^add_tariff_for_product/$', add_tariff_for_product, name='add_tariff_for_product'),
    url(r'^get_tariff_for_product/$', get_tariff_for_product, name='get_tariff_for_product'),

    url(r'^add_pickup_address_for_product/$', add_pickup_address_for_product, name='add_pickup_address_for_product'),
    url(r'^delete_pickup_address_from_product/$', delete_pickup_address_from_product, name='delete_pickup_address_from_product'),

    url(r'^create_new_types_for_categories/$', create_new_types_for_categories, name='create_new_types_for_categories'),
    url(r'^add_types_for_product/$', add_types_for_product, name='add_types_for_product'),
    url(r'^delete_types_from_product/$', delete_types_from_product, name='delete_types_from_product'),

    url(r'^get_all_groups/$', get_all_groups, name='get_all_groups'),
    url(r'^get_all_categories_for_group/$', get_all_categories_for_group, name='get_all_categories_for_group'),
    url(r'^get_all_types_in_category/$', get_all_types_in_category, name='get_all_types_in_category'),
    url(r'^get_all_subcategories_for_category', get_all_subcategories_for_category, name='get_all_subcategories_for_category'),
    url(r'^get_path_for_subcategory', get_path_for_subcategory, name='get_path_for_subcategory'),
    url(r'^get_all_categories', get_all_categories, name='get_all_categories'),
    url(r'^get_all_subcategories', get_all_subcategories, name='get_all_subcategories'),
    url(r'^find_subcategory_by_name', find_subcategory_by_name, name='find_subcategory_by_name'),
    url(r'^get_catalog_tree', get_catalog_tree, name='get_catalog_tree'),

    url(r'^add_class_for_product', add_class_for_product, name='add_class_for_product'),
    url(r'^del_class_for_product', del_class_for_product, name='del_class_for_product'),
    url(r'^get_product_class', get_product_class, name='get_product_class'),

    url(r'^add_type_for_product', add_type_for_product, name='add_type_for_product'),
    url(r'^del_type_for_product', del_type_for_product, name='del_type_for_product'),

    url(r'^add_tags_for_product', add_tags_for_product, name='add_tags_for_product'),
    url(r'^del_tags_from_product', del_tags_from_product, name='del_tags_from_product'),
    url(r'^get_tags_for_product', get_tags_for_product, name='get_tags_for_product'),

    url(r'^add_product_to_my_best_products', add_product_to_my_best_products, name='add_product_to_my_best_products'),
    url(r'^delete_product_from_my_best_products', delete_product_from_my_best_products, name='delete_product_from_my_best_products'),
    url(r'^get_all_my_best_products', get_all_my_best_products, name='get_all_my_best_products'),

    url(r'^add_or_change_pickup_workday', add_or_change_pickup_workday, name='add_or_change_pickup_workday'),
    url(r'^delete_pickup_workday', delete_pickup_workday, name='delete_pickup_workday'),
    url(r'^get_pickup_workdays', get_pickup_workdays, name='get_pickup_workdays'),

    url(r'^add_or_update_about_me', add_or_update_about_me, name='add_or_update_about_me'),
    url(r'^get_about_business', get_about_business, name='get_about_business'),
    url(r'^delete_about_me', delete_about_me, name='delete_about_me'),
    url(r'^add_photo_for_about_business', add_photo_for_about_business, name='add_photo_for_about_business'),
    url(r'^delete_photo_from_about_business', delete_photo_from_about_business, name='delete_photo_from_about_business'),
    url(r'^get_photos_about_business', get_photos_about_business, name='get_photos_about_business'),
    url(r'^get_farmers_best_products', get_farmers_best_products, name='get_farmers_best_products'),
    url(r'^get_farm_list', get_farm_list, name='get_farm_list'),

    url(r'^add_product_image', add_product_image, name='add_product_image'),
    url(r'^update_product_image', update_product_image, name='update_product_image'),
    url(r'^delete_product_image', delete_product_image, name='delete_product_image'),

    url(r'^available_product_list', available_product_list, name='available_product_list'),
    # url(r'^product_list', product_list, name='product_list'),

    url(r'^add_profile_group_product', add_profile_group_product, name='add_profile_group_product'),
    url(r'^delete_profile_group_product', delete_profile_group_product, name='delete_profile_group_product'),
    url(r'^add_profile_category_product', add_profile_category_product, name='add_profile_category_product'),
    url(r'^delete_profile_category_product', delete_profile_category_product, name='delete_profile_category_product'),
    url(r'^add_profile_subcategory_product', add_profile_subcategory_product, name='add_profile_subcategory_product'),
    url(r'^delete_profile_subcategory_product', delete_profile_subcategory_product, name='delete_profile_subcategory_product'),
    url(r'^get_ten_random_products', get_ten_random_products, name='get_ten_random_products'),

    url(r'^filter_products/(?P<group>[A-Za-z_]+)/(?P<category>[A-Za-z_]+)/(?P<subcategory>[A-Za-z_]+)/', filter_products),
    url(r'^filter_products/(?P<group>[A-Za-z_]+)/(?P<category>[A-Za-z_]+)/', filter_products),
    url(r'^filter_products/(?P<group>[A-Za-z_]+)/', filter_products),
    url(r'^filter_products', filter_products, name='filter_products'),
]

