import re
from models import CourierType, Courier, Order


def validate_hour(element):
    if type(element) != str:
        return None
    
    pattern = r'^([0-1]\d|2[0-3]):[0-5][0-9]-([0-1]\d|2[0-3]):[0-5][0-9]$'
    if re.match(pattern, element) is None:
        return None

    return element


def validate_hours(hours):
    if type(hours) != list:
        return None
    for e in hours:
        if validate_hour(e) is None:
            return None
    return(hours)


def validate_regions(regions):
    if type(regions) != list:
        return None
    for e in regions:
        if validate_int(e) is None:
            return None
    return regions


def validate_int(element):
    if type(element) == int:
        return element
    return None


def validate_type(element):
    if element == 'foot':
        return CourierType.foot
    elif element == 'bike':
        return CourierType.bike
    elif element == 'car':
        return CourierType.car
    else:
        return None


def validate_weight(weight):
    if type(weight) != float and type(weight) != int:
        return None
    if weight < 0.01 or weight > 50:
        return None
    else:
        return float(weight)


def validate_courier(courier_dict):
    id = validate_int(courier_dict.get('courier_id'))
    if id is None:
        return None

    t = validate_type(courier_dict.get('courier_type'))
    if t is None:
        return None

    regions = validate_regions(courier_dict.get('regions'))
    if regions is None:
        return None

    hours = validate_hours(courier_dict.get('working_hours'))
    if hours is None:
        return None
    
    return Courier(id, t, regions, hours)


def validate_order(order_dict):
    id = validate_int(order_dict.get('order_id'))
    if id is None:
        return None

    w = validate_weight(order_dict.get('weight'))
    if w is None:
        return None

    reg = validate_int(order_dict.get('region'))
    if reg is None:
        return None

    hours = validate_hours(order_dict.get('delivery_hours'))
    if hours is None:
        return None

    o = Order(id, w, reg, hours)
    return o


s = {
    "courier_id": 1,
    "courier_type": "foot",
    "regions": [1, 12, 22],
    "working_hours": ["11:35-14:05", "09:00-11:00"]
}


s2 = {
"order_id": 3,
"weight": 0.01,
"region": 22,
"delivery_hours": ["09:00-12:00", "16:00-21:30"]
}
