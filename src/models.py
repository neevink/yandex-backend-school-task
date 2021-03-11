import enum
from exceptions import IllegalArgumentError


class CourierType(enum.Enum):
    foot = 10
    bike = 15
    car = 50



class TimeInterval():
    def __init__(self, start_hour, start_minute, end_hour, end_minute):
        if end_hour < 0 or end_hour > 23 or start_hour < 0 or start_hour > 23:
            raise IllegalArgumentError("Количество часов должно быть в интервале от [0; 23]")

        if start_minute < 0 or start_minute > 59 or end_minute < 0 or end_minute > 59:
            raise IllegalArgumentError("Количество часов должно быть в интервале от [0; 59]")

        self.start_time = start_hour * 60 + start_minute
        self.end_time = end_hour * 60 + end_minute

    def __lt__(self, other):
        if self.start_time == other.start_time:
            return self.end_time < other.end_time
        else:
            return self.start_time < other.start_time
    
    def __eq__(self, other):
        return self.start_time == other.start_time and self.end_time == other.end_time

    def __repr__(self):
        return self.__str__()
        
    def __str__(self):
        return "{:0>2}:{:0>2}-{:0>2}:{:0>2}".format(self.start_time // 60, self.start_time % 60, self.end_time // 60, self.end_time % 60)


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
            "working_hours": [str(e) for e in self.working_hours]
        }

    def to_db_entity(self):
        return (
            self.courier_id,
            self.courier_type.value,
            self.regions,
            [[e.start_time, e.end_time] for e in self.working_hours]
        )

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
            "delivery_hours": [str(e) for e in self.delivery_hours]
        }

    
    def to_db_entity(self):
        return (
            self.order_id,
            self.weight,
            self.region,
            [[e.start_time, e.end_time] for e in self.delivery_hours]
        )

    def __str__(self):
        return "({0}, {1}, {2}, {3})".format(self.order_id, self.weight, self.region, self.delivery_hours)
