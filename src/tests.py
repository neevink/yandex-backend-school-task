import unittest
import services
import dal
from models import Courier, CourierType, TimeInterval, Order

class TestServices(unittest.TestCase):
    def setUp(self):
        # Перед каждым запуском теста, чистим бд
        dal.init_database(True)


    @classmethod
    def tearDownClass(cls):
        # После выполнения всех тестов снова чистим бд
        dal.init_database(True)


    # Модульный тест на добавлиение навых курьеров
    def test_inserting_couriers(self):
        c1 = Courier(1, CourierType.foot, [1, 2], [TimeInterval(9, 0, 12, 0), TimeInterval(14, 0, 17, 0)])
        c2 = Courier(2, CourierType.bike, [2, 3], [TimeInterval(10, 0, 16, 0)])
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


    # Модульный тест на добавлиение навых курьеров
    def test_inserting_orders(self):
        o1 = Order(1, 4.67, 2, [TimeInterval(10, 0, 15, 0), TimeInterval(20, 10, 21, 40)])
        o2 = Order(2, 11.5, 3, [TimeInterval(3, 00, 6, 00), TimeInterval(14,0, 17, 00)])
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


    # Модульный тест на назначение новых заказов
    def test_assigning_orders(self):
        c1 = Courier(1, CourierType.foot, [1, 2], [TimeInterval(9, 0, 12, 0), TimeInterval(14, 0, 17, 0)])
        c2 = Courier(2, CourierType.bike, [2, 3], [TimeInterval(10, 0, 16, 0)])
        c3 = Courier(3, CourierType.foot, [2], [TimeInterval(1, 30, 2, 10), TimeInterval(7, 0, 13, 0)])
        c4 = Courier(4, CourierType.foot, [1, 2, 3], [TimeInterval(5, 0, 10, 0)])
        c5 = Courier(5, CourierType.car, [1, 3], [TimeInterval(15, 0, 19, 0), TimeInterval(10, 0, 11, 0)])
        c6 = Courier(6, CourierType.car, [1, 2, 3], [])
        c7 = Courier(7, CourierType.foot, [], [TimeInterval(3, 0, 15, 00)])                
        services.add_couriers([c1, c2, c3, c4, c5, c6, c7])

        o1 = Order(1, 4.67, 2, [TimeInterval(10, 0, 15, 0), TimeInterval(22, 10, 22, 40)])
        o2 = Order(2, 11.5, 3, [TimeInterval(3, 0, 6, 0), TimeInterval(14, 0, 17, 0)])
        o3 = Order(3, 5.44, 2, [TimeInterval(10, 0, 12, 0), TimeInterval(21, 0, 3, 40), TimeInterval(6, 0, 8, 0)])
        o4 = Order(4, 3.33, 3, [TimeInterval(6, 0, 7, 0), TimeInterval(10, 0, 11, 0), TimeInterval(12, 0, 13, 0)])
        o5 = Order(5, 1.5, 1, [TimeInterval(6, 10, 7, 40), TimeInterval(23, 0, 2, 0)])
        o6 = Order(6, 29, 1, [TimeInterval(15, 0, 1, 0)])
        o7 = Order(7, 7.3, 2, [])
        services.add_orders([o1, o2, o3, o4, o5, o6, o7])

        # Отсутствуеют регионы и/или время работы
        ids6 = services.assign_orders(6)
        ids7 = services.assign_orders(7)
        self.assertEqual(ids6, [])
        self.assertEqual(ids7, [])

        # Если не закончен текущий развоз, то назначенные заказы сохраняются
        ids1 = services.assign_orders(1)[0] # [0] - список id, [1] - время
        self.assertEqual(ids1, [1])
        ids1 = services.assign_orders(1)
        self.assertEqual(ids1, [1])

        ids2 = services.assign_orders(2)[0] # [0] - список id, [1] - время
        self.assertEqual(ids2, [3, 4])

        ids3 = services.assign_orders(3)
        self.assertEqual(ids3, [])

        ids4 = services.assign_orders(4)[0] # [0] - список id, [1] - время
        self.assertEqual(ids4, [5])

        ids5 = services.assign_orders(5)[0] # [0] - список id, [1] - время
        self.assertEqual(ids5, [2, 6])


    # Модульный тест на обновление информации о курьере
    def test_updating_courier(self):
        c1 = Courier(1, CourierType.bike, [1, 2], [TimeInterval(9, 0, 12, 0), TimeInterval(14, 0, 17, 0)])
        services.add_couriers([c1])

        o1 = Order(1, 4.5, 1, [TimeInterval(6, 0, 7, 0), TimeInterval(10, 0, 13, 0)])
        o2 = Order(2, 3.5, 2, [TimeInterval(0, 0, 3, 0), TimeInterval(15, 0, 15, 30)])
        o3 = Order(3, 3.7, 1, [TimeInterval(3, 0, 8, 0), TimeInterval(10, 0, 11, 0)])
        services.add_orders([o1, o2, o3])

        ids = services.assign_orders(c1.courier_id) # назначены [1, 2, 3]
        self.assertEqual(ids[0], [1, 2, 3])

        # изменяем грузоподъёмность
        c1 = services.get_courier_by_id(c1.courier_id)
        c1.courier_type = CourierType.foot

        services.update_courier(c1)
        c1_updated = services.get_courier_by_id(c1.courier_id)
        self.assertEqual(c1.courier_id, c1_updated.courier_id)
        self.assertEqual(c1.courier_type, c1_updated.courier_type)

        ids = services.assign_orders(c1.courier_id)
        self.assertEqual(ids, [2, 3]) # Должен отмениться заказ #1 из-за веса

        # изменяем регион
        c1 = services.get_courier_by_id(c1.courier_id)
        c1.regions = [2, 3]

        services.update_courier(c1)
        c1_updated = services.get_courier_by_id(c1.courier_id)
        self.assertEqual(c1.courier_id, c1_updated.courier_id)
        self.assertEqual(c1.regions, c1_updated.regions)

        ids = services.assign_orders(c1.courier_id)
        self.assertEqual(ids, [2]) # Должен отмениться заказ #3 из-за региона

        # изменяем время работы
        c1 = services.get_courier_by_id(c1.courier_id)
        c1.working_hours = [TimeInterval(4, 0, 6, 0), TimeInterval(12, 30, 13, 30)]

        services.update_courier(c1)
        c1_updated = services.get_courier_by_id(c1.courier_id)
        self.assertEqual(c1.courier_id, c1_updated.courier_id)
        self.assertEqual(c1.working_hours, c1_updated.working_hours)

        ids = services.assign_orders(c1.courier_id)
        self.assertEqual(ids, []) # Должен отмениться заказ #2 из-за времени

        # Проверка на доступность выдачи заказов другому курьеру
        c2 = Courier(2, CourierType.bike, [1, 2], [TimeInterval(9, 0, 12, 0), TimeInterval(14, 0, 17, 0)])
        services.add_couriers([c2])
        ids = services.assign_orders(c2.courier_id)
        self.assertEqual(ids[0], [1, 2, 3])


class TestDAL(unittest.TestCase):
    def setUp(self):
        # Перед каждым запуском теста, чистим бд
        dal.init_database(True)


    @classmethod
    def tearDownClass(cls):
        # После выполнения всех тестов снова чистим бд
        dal.init_database(True)


    # Модульный тест на нахождение пересечений в интервалах времени
    def test_intersection_of_time(self):
        t1 = [TimeInterval(15, 0, 16, 0)]
        t2 = [TimeInterval(16, 0, 15, 0)]
        t1 = [(e.start_time, e.end_time) for e in t1]
        t2 = [(e.start_time, e.end_time) for e in t2]

        b1 = dal.try_assign_order(dal.prepare_list_of_intervals(t1), dal.prepare_list_of_intervals(t2))
        self.assertFalse(b1)

        t3 = [TimeInterval(10, 55, 11, 43)]
        t4 = [TimeInterval(11, 40, 11, 45)]
        t3 = [(e.start_time, e.end_time) for e in t3]
        t4 = [(e.start_time, e.end_time) for e in t4]

        b2 = dal.try_assign_order(dal.prepare_list_of_intervals(t3), dal.prepare_list_of_intervals(t4))
        self.assertTrue(b2)

        t5 = [TimeInterval(3, 30, 4, 40), TimeInterval(6, 0, 9, 0), TimeInterval(11, 0, 12, 50)]
        t6 = [TimeInterval(1, 20, 2, 59), TimeInterval(7, 20, 8, 33), TimeInterval(17, 30, 19, 20)]
        t5 = [(e.start_time, e.end_time) for e in t5]
        t6 = [(e.start_time, e.end_time) for e in t6]

        b3 = dal.try_assign_order(dal.prepare_list_of_intervals(t5), dal.prepare_list_of_intervals(t6))
        self.assertTrue(b3)

        t7 = [TimeInterval(2, 33, 10, 55)]
        t8 = [TimeInterval(10, 55, 2, 33)]
        t7 = [(e.start_time, e.end_time) for e in t7]
        t8 = [(e.start_time, e.end_time) for e in t8]

        b4 = dal.try_assign_order(dal.prepare_list_of_intervals(t7), dal.prepare_list_of_intervals(t8))
        self.assertFalse(b4)

        t9 = [TimeInterval(18, 0, 20, 0), TimeInterval(23, 40, 2, 10)]
        t10 = [TimeInterval(21, 0, 22, 15), TimeInterval(0, 0, 3, 20)]
        t9 = [(e.start_time, e.end_time) for e in t9]
        t10 = [(e.start_time, e.end_time) for e in t10]

        b5 = dal.try_assign_order(dal.prepare_list_of_intervals(t9), dal.prepare_list_of_intervals(t10))
        self.assertTrue(b5)


if __name__ == '__main__':
    unittest.main()