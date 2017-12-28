def json_address(addr):
    # генерирует json для адреса
    if not addr:
        return {}

    return {
        "id": addr.id,
        "type": type(addr).__name__,
        "exist_city": addr.content_type.model,
        "city": addr.city.name_en if addr.city else None,
        "region": addr.city.region.name_en if addr.city and addr.city.region else None,
        "country": addr.city.region.country.name_en if addr.city and addr.city.region else None,
        "address": addr.address,
        "address_name": addr.name,
        "default_address": addr.default,
        "postal_code": addr.postal_code,
        "city_id": addr.city.id if addr.city else None,# if addr.content_type.model != 'notexistcity' else '',
        "region_id": addr.city.region.id if addr.city else None,# if addr.content_type.model != 'notexistcity' else '',
        "country_id": addr.city.region.country.id if addr.city else None
    }


def json_work_time(work_time):
    if not work_time:
        return {}

    return {
        "day": work_time.day,
        "open": work_time.open.strftime('%H:%M'),
        "close": work_time.close.strftime('%H:%M'),
        "break_start": work_time.break_start.strftime('%H:%M') if work_time.break_start else None,
        "break_stop": work_time.break_stop.strftime('%H:%M') if work_time.break_stop else None,
        "pickup_id": work_time.pickup.id
    }
