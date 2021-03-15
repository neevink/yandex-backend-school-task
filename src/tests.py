import unittest
import services
from models import Courier, CourierType, TimeInterval, Order

class TestServices(unittest.TestCase):

    def test_inserting_couriers(self):
        c1 = Courier(1, CourierType.foot, [1, 2, 3], [TimeInterval(9, 0, 12, 0), TimeInterval(14, 0, 17, 0)])
        c2 = Courier(2, CourierType.bike, [2, 1], [TimeInterval(11, 0, 15, 0)])
        services.add_couriers([c1, c2])

        c1_from_db = services.get_courier_by_id(c1.courier_id)
        self.assertEqual(c1.courier_id, c1_from_db.courier_id)
        self.assertEqual(c1.courier_type, c1_from_db.courier_type)
        self.assertEqual(c1.regions, c1_from_db.regions)
        self.assertEqual(c1.working_hours, c1_from_db.working_hours)

        c2_from_db = services.get_courier_by_id(c2.courier_id)
        self.assertEqual(c2.courier_id, c2_from_db.courier_id)
        self.assertEqual(c2.courier_type, c2_from_db.courier_type)
        self.assertEqual(c2.regions, c2_from_db.regions)
        self.assertEqual(c2.working_hours, c2_from_db.working_hours)


    def test_updating_courier(self):
        c1 = services.get_courier_by_id(1)
        c1.courier_type = CourierType.car
        c1.regions = [2, 3]
        c1.working_hours = [TimeInterval(9, 15, 12, 30), TimeInterval(14, 40, 17, 30)]

        services.update_courier(c1)
        c1_updated = services.get_courier_by_id(c1.courier_id)
        self.assertEqual(c1.courier_id, c1_updated.courier_id)
        self.assertEqual(c1.courier_type, c1_updated.courier_type)
        self.assertEqual(c1.regions, c1_updated.regions)
        self.assertEqual(c1.working_hours, c1_updated.working_hours)


    def test_inserting_orders(self):
        o1 = Order(5, 5, 2, [TimeInterval(8, 33, 11, 44), TimeInterval(20, 13, 21, 15), TimeInterval(23, 40, 3, 20)])
        o2 = Order(6, 6.5, 3, [TimeInterval(9, 45, 19, 25), TimeInterval(22,0, 4, 00)])
        services.add_orders([o1, o2])

        o1_from_db = services.get_order_by_id(o1.order_id)
        self.assertEqual(o1.order_id, o1_from_db.order_id)
        self.assertEqual(o1.weight, o1_from_db.weight)
        self.assertEqual(o1.region, o1_from_db.region)
        self.assertEqual(o1.delivery_hours, o1_from_db.delivery_hours)

        o2_from_db = services.get_order_by_id(o2.order_id)
        self.assertEqual(o2.order_id, o2_from_db.order_id)
        self.assertEqual(o2.weight, o2_from_db.weight)
        self.assertEqual(o2.region, o2_from_db.region)
        self.assertEqual(o2.delivery_hours, o2_from_db.delivery_hours)


    def test_assigning_orders(self):
        c1 = Courier(10, CourierType.car, [1, 2, 3], [TimeInterval(9, 0, 12, 0), TimeInterval(14, 0, 17, 0)])
        c2 = Courier(11, CourierType.bike, [1, 2], [TimeInterval(1, 0, 23, 0)])
        c3 = Courier(12, CourierType.bike, [2, 3], [TimeInterval(21, 00, 1, 30)])
        services.add_couriers([c1, c2, c3])

        o1 = Order(10, 4.33, 1, [TimeInterval(9, 0, 10, 0), TimeInterval(16, 0, 18, 0), TimeInterval(5,0,11,00)])
        o2 = Order(11, 2.50, 3, [TimeInterval(9, 0, 19, 0)])
        o3 = Order(12, 17.66, 2, [TimeInterval(8, 0, 10, 0), TimeInterval(20, 0, 21, 0)])
        o4 = Order(13, 6.5, 2, [TimeInterval(23, 0, 2, 30)])
        services.add_orders([o1, o2, o3, o4])

        ids = services.assign_orders(10)[0] # [0] - список id, [1] - время
        self.assertEqual(ids, [10, 11, 12])

        ids = services.assign_orders(11)[0]
        self.assertEqual(ids, [13])

        ids = services.assign_orders(11)[0]
        self.assertEqual(ids, [])

        ids = services.assign_orders(12)[0]
        self.assertEqual(ids, [])


if __name__ == '__main__':
    unittest.main()