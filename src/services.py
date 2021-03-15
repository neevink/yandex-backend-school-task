import dal
from datetime import datetime

from models import Courier, CourierType, Order, TimeInterval


def add_couriers(list_of_couriers):
    try:
        dal.add_couriers(list_of_couriers)
    except Exception as e:
        raise Exception('Произошла ошибка: ' + str(e))


def add_orders(list_of_orders):
    try:
        dal.add_orders(list_of_orders)
    except Exception as e:
        raise Exception('Произошла ошибка: ' + str(e))


# Получить курьера по идентификатору
def get_courier_by_id(courier_id):
    courier = None
    try:
        courier = dal.select_courier_by_id(courier_id)
    except Exception as e:
        raise Exception('Произошла ошибка: ' + str(e))
    return courier


# Получить заказ по идентификатору
def get_order_by_id(order_id):
    try:
        order = dal.select_order_by_id(order_id)
    except Exception as e:
        raise Exception('Произошла ошибка: ' + str(e))
    return order


def update_courier(courier):
    try:
        dal.update_courier(courier)
    except Exception as e:
        raise Exception('Произошла ошибка: ' + str(e))


def assign_orders(courier_id):
    orders_ids = dal.select_orders_for_courier(courier_id)
    orders_ids.sort()

    assign_time = dal.get_assign_time_for_courier(courier_id)
    for id in orders_ids:
        dal.assign_order(courier_id, id, assign_time)

    return (orders_ids, assign_time)


# Перебуру все заказы, и назначу заказ курьеру, если интервалы времени в которые он работает
# содержатся в интервалах кремени, когда заказчик может принять товар. Таким образом задача
# сводится к задаче покрытия интервалов.

# Согласно имеющейся у меня информации, заказ назначить можно, если выполняются условя:
# 1) курьер работает в этом регионе
# 2) вес заказа меньше или равен грузоподъёмности
# 3) есть хотя бы одно ненуливое прересечение интервалов времени доставки заказа и интервалов времени работы курьера
# 4) суммарный вес заказов, выдаваемых курьеру за раз должен быть меньше или равен грузоподъёмности


'''
c1 = Courier(10, CourierType.car, [1, 2, 3], [TimeInterval(9, 0, 12, 0), TimeInterval(14, 0, 17, 0)])
c2 = Courier(11, CourierType.bike, [1, 2], [TimeInterval(21, 0, 5, 0)])
c3 = Courier(12, CourierType.bike, [2, 3], [TimeInterval(21, 00, 1, 30)])
add_couriers([c1, c2, c3])

o1 = Order(10, 4.33, 1, [TimeInterval(9, 0, 10, 0), TimeInterval(16, 0, 18, 0), TimeInterval(5,0,11,00)])
o2 = Order(11, 2.50, 3, [TimeInterval(9, 0, 19, 0)])
o3 = Order(12, 17.66, 2, [TimeInterval(8, 0, 10, 0), TimeInterval(20, 0, 21, 0)])
o4 = Order(13, 6.5, 2, [TimeInterval(23, 0, 2, 30)])
add_orders([o1, o2, o3, o4])

ids = assign_orders(10)[0] # [0] - список id, [1] - время
print(ids)

ids = assign_orders(11)[0]
print(ids)

ids = assign_orders(11)[0]
print(ids)
'''

t = datetime(2021, 1, 10, 9, 32, 14, 420000).isoformat()[:-4]+'Z'
print(t)

s = '2021-01-10T09:32:14.42Z'
t2 = datetime.strptime('2021-01-10T09:32:14.42Z', "%Y-%m-%dT%H:%M:%S.%fZ")
print(t2)