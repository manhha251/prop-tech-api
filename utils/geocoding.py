from geopy.geocoders import Nominatim
import requests
import re
from functools import lru_cache

geolocator = Nominatim(user_agent='utils')
administrative_units = {'tỉnh': 'province',
                        'thành phố': 'city',
                        'thành phố trực thuộc trung ương': 'city',
                        'thành phố thuộc thành phố trực thuộc trung ương': 'city',
                        'quận': 'district',
                        'huyện': 'district',
                        'thị xã': 'town',
                        'thành phố thuộc tỉnh': 'city',
                        'phường': 'ward',
                        'xã': 'commune',
                        'đường': 'street'}


def pre_process_address(full_address: str):
    address = full_address.split(', ')

    for i in range(len(address)):
        for vi, en in administrative_units.items():
            if address[i].lower().startswith(vi):
                address[i] = re.sub(vi, '', address[i], flags=re.IGNORECASE).strip()
                if en != 'street':
                    if address[i].strip().lower() == u'thủ đức':
                        address[i] += ' ' + 'city'
                    elif not address[i].isnumeric():
                        address[i] += ' ' + en
                    else:
                        address[i] = en + ' ' + address[i]
                break
        address[i].strip()

    return ', '.join(address)


@lru_cache(maxsize=65536)
def geocode(address: str):
    new_address = pre_process_address(address)
    coordinate = geolocator.geocode(query=new_address, country_codes='VN', timeout=100)

    if coordinate is not None:
        return coordinate.latitude, coordinate.longitude
    else:
        return None, None
