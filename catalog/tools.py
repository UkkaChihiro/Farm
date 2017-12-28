from catalog.models import ProductType, TagsForProduct, ImgProduct, ClassProduct


def sintez_json_from_product(obj):
    #генерирует json для продукта со всеми полями
    all_type_prod = ProductType.objects.filter(product=obj)
    type_prod = [{"id": t.type.id, "name": t.type.name} for t in all_type_prod]

    all_tags_prod = TagsForProduct.objects.filter(product=obj)
    tags_prod = [{t.id: t.name} for t in all_tags_prod]

    all_classes_prod = ClassProduct.objects.filter(product=obj)
    class_prod = [c.name for c in all_classes_prod]

    all_photos = ImgProduct.objects.filter(product=obj)
    all_photos = [{"id": p.id, "url": p.img.url, "avatar": p.avatar, "created": p.created.strftime('%H:%M:%S %Y-%m-%d')} for p in all_photos]

    if obj.discount_price:
        discount_price = str(obj.discount_price.amount)
    else:
        discount_price = '0'
    cost = round(float(obj.price.amount) / obj.weight_of_pack, 2)
    discount_cost = round(float(obj.discount_price.amount) / obj.weight_of_pack, 2) if obj.discount_price else None

    return {
        "id": obj.id,
        "profile_business": obj.profile_business.id,
        "name": obj.name,
        "name_en": obj.name_en,
        "description": obj.description,
        "description_en": obj.description_en,
        "number_of_packages": obj.number_of_packages,
        "weight_of_pack": obj.weight_of_pack,
        "nondurable": obj.nondurable,
        "measure": obj.measure,
        "measure_count": obj.measure_count,
        "price": str(obj.price.amount),
        "discount_price": discount_price,
        "currency_name": obj.currency.name,
        "currency_id": obj.currency.id,
        "subcategory_id": obj.category.id,
        "subcategory_name": obj.category.name,
        "country_id": obj.country.id if obj.country else "",
        "country": obj.country.name_en if obj.country else "",
        "region": obj.region,
        "video": obj.video,
        "active": obj.active,
        "checked": obj.checked,
        "mark_deleted": obj.mark_deleted,
        "updated_at": obj.updated_at.strftime('%H:%M:%S %Y-%m-%d'),
        "created_at": obj.created_at.strftime('%H:%M:%S %Y-%m-%d'),
        "start_of_sales_date": obj.start_of_sales_date.strftime('%Y-%m-%d') if obj.start_of_sales_date else "",
        "end_of_sales_date": obj.end_of_sales_date.strftime('%Y-%m-%d') if obj.end_of_sales_date else "",
        "expiry_days": obj.expiry_days,
        "classes": class_prod,
        "types": type_prod,
        "tags": tags_prod,
        "photos": all_photos,
        "cost_for_100gr": cost,
        "disc_cost_for_100gr": discount_cost

    }


def short_prod(obj):
    all_classes_prod = ClassProduct.objects.filter(product=obj)
    class_prod = [c.name for c in all_classes_prod]

    all_type_prod = ProductType.objects.filter(product=obj)
    type_prod = [{"id": t.type.id, "name": t.type.name} for t in all_type_prod]

    avatar = ImgProduct.objects.filter(product=obj, avatar=True).first()

    return {
        "id": obj.id,
        "name": obj.name,
        "name_en": obj.name_en,
        "price": str(obj.price.amount),
        "currency": str(obj.price.currency),
        "discount_price": str(obj.discount_price.amount) if obj.discount_price else None,
        "d_price_currency": str(obj.discount_price.currency) if obj.discount_price else None,
        "avatar": avatar.img.url if avatar else None,
        "types": type_prod,
        "classes": class_prod,
        "subcategory_id": obj.category.id,
        "subcategory_name": obj.category.name
    }
