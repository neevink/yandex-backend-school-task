import unittest
import services
from models import Courier, CourierType, TimeInterval, Order

class TestServices(unittest.TestCase):
    def setUp(self):
        pass


    def test_inserting_couriers(self):
        c1 = Courier(1, CourierType.foot, [1, 2, 3], [TimeInterval(9, 0, 12, 0), TimeInterval(14, 0, 17, 0)])
        c2 = Courier(2, CourierType.bike, [1, 3], [TimeInterval(11, 0, 15, 0)])
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
        o1 = Order(1, 4.33, 2, [TimeInterval(8, 0, 10, 0), TimeInterval(20, 0, 21, 0)])
        o2 = Order(2, 2.50, 3, [TimeInterval(9, 0, 19, 0)])
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



if __name__ == '__main__':
    unittest.main()