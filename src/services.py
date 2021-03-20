import dal
from datetime import datetime

from models import Courier, CourierType, Order, TimeInterval


# Добавить курьеров
def add_couriers(list_of_couriers):
    try:
        dal.add_couriers(list_of_couriers)
    except Exception as e:
        raise Exception('Произошла ошибка: ' + str(e))


# Добавить заказы
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


def is_couriers_contains_ids(list_of_courier_ids):
    return dal.is_couriers_contains_ids(list_of_courier_ids)


def is_orders_contains_ids(list_of_order_ids):
    return dal.is_orders_contains_ids(list_of_order_ids)


def assign_orders(courier_id):
    # Проверить, есть ли незаконченный развоз
    if not dal.is_delivery_finished(courier_id):
        # Возвращаем список неразвезённых заказов
        not_finished_ids = dal.select_not_finished_assignments(courier_id)
        return [e[0] for e in not_finished_ids]

    orders_ids = dal.select_orders_for_courier(courier_id)
    if len(orders_ids) == 0:
        return ([]) # Вернуть пустой список, время возвращать не нужно

    orders_ids.sort()

    # Округлим миллисикунды до 2х цифр для текущего времени
    assign_time = datetime.now()
    assign_time = assign_time.replace(microsecond = assign_time.microsecond // 10000 * 10000)

    dal.assign_orders(courier_id, orders_ids, assign_time)

    return (orders_ids, assign_time)


# Отметить заказ, как выполненный
def complete_order(courier_id, order_id, complete_time):
    if not dal.is_order_assigned_for_courier(courier_id,order_id):
        raise Exception('Заказ или курьер не найден или заказ не назначен этому курьеру')

    # Если заказ уже выполнен, то перезаписывать время выполнения не нужно
    if not dal.is_order_completed(courier_id, order_id):
        return order_id
    
    dal.complete_order(courier_id,order_id, complete_time)

    # Если все заказы выполнены, то отмечаем выполненым развоз
    if dal.is_completed_all_assignments(courier_id):
        delivery_id = dal.get_not_finished_delivery(courier_id)
        dal.complete_delivery(delivery_id)

    return order_id


# Посчитать заработную плату курьера
def calcuate_courier_sallary(courier_id):
    return dal.calcuate_courier_sallary(courier_id)


# Посчитать рейтинг курьера
def calculate_courier_rating(courier_id):
    return dal.get_courier_rating(courier_id)


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

'''
t = datetime(2021, 1, 10, 9, 32, 14, 420000).isoformat()[:-4]+'Z'
print(t)

s = '2021-01-10T09:32:14.42Z'
t2 = datetime.strptime('2021-01-10T09:32:14.42Z', "%Y-%m-%dT%H:%M:%S.%fZ")
print(t2)
'''

'''
print(assign_orders(2))
tiem = datetime.now()
tiem = tiem.replace(microsecond = tiem.microsecond // 10000 * 10000)
print(complete_order(2, 21, tiem))

print(assign_orders(2))


print(calcuate_courier_sallary(2))
print(calculate_courier_rating(2))
'''



'''
print(assign_orders(2))
tiem = datetime.now()
tiem = tiem.replace(microsecond = tiem.microsecond // 10000 * 10000)
print(complete_order(2, 10, tiem))

print(assign_orders(2))


print(calcuate_courier_sallary(2))
print(calculate_courier_rating(2))

'''