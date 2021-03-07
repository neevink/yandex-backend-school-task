
couriers = []

def get_all_couriers():
    return couriers

def get_courier(id):
    c = list(filter(lambda x: x.courier_id == id, couriers))
    if len(c) == 0:
        return None
    else:
        return c[0]
