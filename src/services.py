import dal


def add_couriers(list_of_couriers):
    try:
        dal.add_couriers(list_of_couriers)
    except Exception as e:
        print('Произошла ошибка: ' + e)


def add_orders(list_of_orders):
    try:
        dal.add_orders(list_of_orders)
    except Exception as e:
        print('Произошла ошибка: ' + e)


# Получить курьера по идентификатору
def get_courier_by_id(courier_id):
    try:
        courier = dal.select_courier_by_id(courier_id)
    except Exception as e:
        print('Произошла ошибка: ' + (e))
    return courier


# Получить заказ по идентификатору
def get_order_by_id(order_id):
    try:
        order = dal.select_order_by_id(order_id)
    except Exception as e:
        print('Произошла ошибка: ' + str(e))
    return order


def update_courier(courier):
    try:
        dal.update_courier(courier)
    except Exception as e:
        print('Произошла ошибка: ' + e)


def select_orders_for_courier(courier_id):
    return dal.select_orders_for_courier(courier_id)


# Перебуру все заказы, и назначу заказ курьеру, если интервалы времени в которые он работает
# содержатся в интервалах кремени, когда заказчик может принять товар. Таким образом задача
# сводится к задаче покрытия интервалов.

# Согласно имеющейся у меня информации, заказ назначить можно, если выполняются условя:
# 1) курьер работает в этом регионе
# 2) вес заказа меньше или равен грузоподъёмности
# 3) есть хотя бы одно ненуливое прересечение интервалов времени доставки заказа и интервалов времени работы курьера
# 4) суммарный вес заказов, выдаваемых курьеру за раз должен быть меньше или равен грузоподъёмности


# Может ли курьер выполнить заказ, временные промежутки должны быть отсортированы,
# интервалы, проходящие через 00:00, разбиты на [x; 23:59] U [00:00; y]
def try_assign_order(courier_times, delivery_times):

    i = 0 # индекс временных интервалов курьера
    j = 0 # индекс временных интервалов доставки

    while j < len(delivery_times):
        if i == len(courier_times):
            break

        # Если начало работы курьера позже доставки
        if delivery_times[j][1] < courier_times[i][0]:
            j += 1
            continue
        # Если курьер работает в то время, когда можно осуществить доставку
        if delivery_times[j][0] < courier_times[i][1]:
            return True
        j += 1
    return False
