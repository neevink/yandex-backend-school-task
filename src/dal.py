from models import TimeInterval


couriers = []
orders = []


def add_couriers(list_of_couriers):
    for e in list_of_couriers:
        couriers.append(e)


def get_all_couriers():
    return couriers


def get_courier(id):
    c = list(filter(lambda x: x.courier_id == id, couriers))
    if len(c) == 0:
        return None
    else:
        return c[0]


# Перебуру все заказы, и назначу заказ курьеру, если интервалы времени в которые он работает
# содержатся в интервалах кремени, когда заказчик может принять товар. Таким образом задача
# сводится к задаче покрытия интервалов.

# Может ли курьер выполнить заказ, временные промежутки должны быть отсортированы,
# интервалы, проходящие через 00:00, разбиты на [x; 23:59] U [00:00; y]
def try_assign_order(courier_times, delivery_times):

    i = 0 # индекс временных интервалов курьера
    j = 0 # индекс временных интервалов доставки

    while j < len(delivery_times):
        if i == len(courier_times):
            break

        # Если начало работы курьера позже доставки
        if delivery_times[j].end_time < courier_times[i].start_time:
            j += 1
            continue
        # Если курьер работает в то время, когда можно осуществить доставку
        if delivery_times[j].start_time <= courier_times[i].start_time and courier_times[i].end_time <= delivery_times[j].end_time:
            i += 1
            continue
        # Если у нас курьер может доставить заказ до тоery_times[j].start_time > courier_times[i].start_time:
            return False
        j += 1
    if i == len(courier_times):
        return True
    else:
        return False


# Перебирает список интервалов и разбивает интервалы, если они проходят через 00:00 на интервалы [x; 23:59] U [00:00; y]
def prepare_list_of_intervals(list_of_intervals):
    for e in list_of_intervals:
        if e.end_time < e.start_time:
            list_of_intervals.remove(e)
            list_of_intervals.append(TimeInterval(e.start_time // 60, e.start_time % 60, 23, 59))
            list_of_intervals.append(TimeInterval(0, 0, e.end_time // 60, e.end_time % 60,))
            # Поскольку есть гарантия, что интервалы непересекающиеся, то дальше искать нет смысла
            break
    list_of_intervals.sort()
    return list_of_intervals

# 1 тест
# a = [TimeInterval(16, 39, 17, 52), TimeInterval(23, 13, 1, 3), TimeInterval(2, 10, 3, 0)]
# a = prepare_list_of_intervals(a)
# b = [TimeInterval(16, 0, 23, 59), TimeInterval(0,0,2,0), TimeInterval(2, 10, 4, 0)]
# b.sort()

# 2 тест
#b = [TimeInterval(16,22,23,40), TimeInterval(0, 20, 4, 44)]
#b = prepare_list_of_intervals(b)

# print(try_assign_order(a, b))
