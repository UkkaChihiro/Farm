from farm.models import AddressFarm, FarmGroupMap


def json_farm(farm):
    # генерирует json для фермы
    addr = AddressFarm.objects.filter(profile=farm).first()
    if addr:
        addr = {
            'id': addr.id,
            'city': addr.city.name_en if addr.city else None,
            'region': addr.city.region.name_en if addr.city else None,
            'country': addr.city.region.country.name_en if addr.city else None,
            'address': addr.address,
            'postal_code': addr.postal_code
        }
    out_vars = {
        'id': farm.id,
        'name': farm.name,
        'business_profile': farm.profile.id,
        'groups': [fg.group.id for fg in FarmGroupMap.objects.filter(farm=farm)],
        'address': addr,
    }
    return out_vars
