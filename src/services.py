import dal
from models import Courier, CourierType, Order, TimeInterval
from datetime import datetime


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


# Обновить информацию о курьере (courier_id меняться не может)
def update_courier(courier):
    try:
        dal.update_courier(courier)
    except Exception as e:
        raise Exception('Произошла ошибка: ' + str(e))


# Проверить не содержатся ли курьер с таким id в базе данных
def is_couriers_contains_id(courier_id):
    return dal.is_couriers_contains_id(courier_id)


# Проверить не содержатся ли заказ с таким id в базе данных
def is_orders_contains_id(order_id):
    return dal.is_orders_contains_id(order_id)


# Назначить заказ курьеру
def assign_orders(courier_id):
    # Проверить, есть ли незаконченный развоз
    if not dal.is_delivery_finished(courier_id):
        # Возвращаем список неразвезённых заказов
        not_finished_ids = dal.select_not_finished_assignments(courier_id)

        # Также нужно вернуть время начала незаконченного развоза
        delivery_id = dal.get_not_finished_delivery(courier_id)
        assign_time = dal.get_assign_time(delivery_id)

        return ([e[0] for e in not_finished_ids], assign_time)

    orders_ids = dal.select_orders_for_courier(courier_id)
    if len(orders_ids) == 0:
        return ([])  # Вернуть пустой список, время возвращать не нужно

    orders_ids.sort()

    # Округлим миллисикунды до 2х цифр для текущего времени
    assign_time = datetime.now()
    ms = assign_time.microsecond // 10000 * 10000
    assign_time = assign_time.replace(microsecond=ms)

    dal.assign_orders(courier_id, orders_ids, assign_time)

    return (orders_ids, assign_time)


# Отметить заказ, как выполненный
def complete_order(courier_id, order_id, complete_time):
    if not dal.is_order_assigned_for_courier(courier_id, order_id):
        raise Exception(
            'Заказ или курьер не найден или заказ не назначен этому курьеру')

    # Если заказ уже выполнен, то перезаписывать время выполнения не нужно
    if not dal.is_order_completed(courier_id, order_id):
        return order_id

    dal.complete_order(courier_id, order_id, complete_time)

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
