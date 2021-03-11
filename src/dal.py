from models import TimeInterval, Order, Courier, CourierType
import psycopg2


# Создать подключение к базе данных
def create_db_connection(db_name, db_user, db_password, db_host):
    connection = None
    try:
        connection = psycopg2.connect(
            database = db_name,
            user = db_user,
            password = db_password,
            host = db_host
        )
        print("Подключение к базе данных прошло успешно.")
    except OperationalError as e:
        print(f'Произошла ошибка подключения: ' + e)
    return connection


# Создать таблицы в базе данных, если не существуют
def init_database(connection):
    cursor = connection.cursor()
    # Выпили эту строчку, когда закончишь
    cursor.execute('drop table couriers; drop table orders;')

    # Потом заменить на create table if not exist couriers
    cursor.execute(
    '''
        create table couriers(
            courier_id integer primary key, 
            type integer not null,
            regions integer[] not null,
            working_time integer[][2] not null
        );
        create table orders(
            order_id integer primary key, 
            weight integer not null,
            region integer not null,
            delivery_time integer[][2] not null
        );
    '''
    )
    cursor.close()


# Добавить в базу данных список заказов
def add_orders(connection, orders):
    cursor = connection.cursor()
    values = [e.to_db_entity() for e in orders]
    cursor.execute(
        f'insert into orders (order_id, weight, region, delivery_time) values { ", ".join(["%s"] * len(values)) }',
        values
    )


# Добавить в базу данных список курьеров
def add_couriers(connection, couriers):
    cursor = connection.cursor()
    values = [e.to_db_entity() for e in couriers]
    cursor.execute(
        f'insert into couriers (courier_id, type, regions, working_time) values { ", ".join(["%s"] * len(values)) }',
        values
    )


def select_courier_by_id(connection, courier_id):
    cursor = connection.cursor()
    cursor.execute(
        f"select * from couriers where courier_id = %s", [courier_id]
    )
    result = cursor.fetchall()[0]
    return Courier(result[0], CourierType(result[1]), result[2], result[3])

    
# Тут будут исключения
db_connection = create_db_connection('candy_shop', 'candy_admin', '1', 'localhost')
db_connection.autocommit = True
init_database(db_connection)

o = [Order(1,2,3, [TimeInterval(1,20,2,20), TimeInterval(12,00,15,00)]), Order(2, 10, 5, [TimeInterval(17,30,19,30)])]
add_orders(db_connection, o)

c = [Courier(1, CourierType.foot, [1,2,3], [TimeInterval(1,20,1,50)]), Courier(2, CourierType.car, [2,4], [TimeInterval(10,20,13,40), TimeInterval(14,50,15,50)])]
add_couriers(db_connection, c)

s = select_courier_by_id(db_connection, 2)

print(s)

couriers = []
orders = []


# Всё, что ниже нужно выпилить, потому что тут только работа с данными
# Всё, что ниже вынести в какой-нить сервис
def add_couriers(list_of_couriers):
    for e in list_of_couriers:
        couriers.append(e)


def add_orders(list_of_orders):
    for e in list_of_orders:
        orders.append(e)


def get_all_couriers():
    return couriers


# Вернуть курьера по id
def get_courier_by_id(id):
    for e in couriers:
        if e.courier_id == id:
            return e
    return None


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

import dateutil.parser
z = dateutil.parser.parse('2021-01-10T10:33:01.42Z')
z2 = dateutil.parser.parse('2020-01-10T10:33:01.42Z')

# print(type(z-z2))
