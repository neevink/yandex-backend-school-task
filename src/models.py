import enum


class CourierType(enum.Enum):
    foot = 0
    bike = 1
    car = 2


class Courier():
    def __init__(self, id, t, regions, hours):
        self.courier_id = id
        self.courier_type = t
        self.regions = regions
        self.working_hours = hours

    def to_dict(self):
        if self.courier_type == None:
            tname = None
        else:
            tname = self.courier_type.name

        return {
            "courier_id": self.courier_id,
            "courier_type": tname,
            "regions": self.regions,
            "working_hours": self.working_hours
        }

    def __str__(self):
        return "({0}, {1}, {2}, {3})".format(self.courier_id, self.courier_type, self.regions, self.working_hours)


class Order:
    def __init__(self, id, weight, region, hours):
        self.order_id = id
        self.weight = weight
        self.region = region
        self.delivery_hours = hours

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "weight": self.weight,
            "region": self.region,
            "delivery_hours": self.delivery_hours
        }

    def __str__(self):
        return "({0}, {1}, {2}, {3})".format(self.order_id, self.weight, self.region, self.delivery_hours)

