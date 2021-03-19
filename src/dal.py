from models import TimeInterval, Order, Courier, CourierType
import psycopg2
from datetime import datetime


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


# Создать таблицы в базе данных, если они не существуют
def init_database(drop_db_tables_on_init):
    cursor = db_connection.cursor()

    if drop_db_tables_on_init:
        try:
            cursor.execute('drop table assignments; drop table deliveries; drop table couriers; drop table orders;')
        except:
            print('Дропнуть предыдущие версии бд не удалось :(')

    # Потом заменить на create table if not exist couriers
    cursor.execute(
    '''
        create table if not exists couriers(
            courier_id integer primary key, 
            type integer not null,
            regions integer[] not null,
            working_time integer[][2] not null
        );
        create table if not exists orders(
            order_id integer primary key, 
            weight real not null,
            region integer not null,
            delivery_time integer[][2] not null
        );
        create table if not exists deliveries(
            delivery_id serial primary key,
            assign_time timestamp,
            completed boolean not null default false,
            salary_coefficient integer not null
        );
        create table if not exists assignments(
            courier_id integer references couriers (courier_id),
            order_id integer references orders (order_id),
            delivery_id integer references deliveries (delivery_id) on delete cascade,
            complete_time timestamp,
            wasted_seconds integer,
            completed boolean not null default false,
            primary key (courier_id, order_id)
        );
    '''
    )
    cursor.close()


# Добавить в таблицу orders список новых заказов
def add_orders(orders):
    cursor = db_connection.cursor()
    values = [e.to_db_entity() for e in orders]
    cursor.execute(
        f'insert into orders (order_id, weight, region, delivery_time) values { ", ".join(["%s"] * len(values)) };',
        values
    )
    cursor.close()


# Добавить в таблицу couriers список новых курьеров
def add_couriers(couriers):
    cursor = db_connection.cursor()
    values = [e.to_db_entity() for e in couriers]
    cursor.execute(
        f'insert into couriers (courier_id, type, regions, working_time) values { ", ".join(["%s"] * len(values)) };',
        values
    )
    cursor.close()


# Получить курьера по id
def select_courier_by_id(courier_id):
    cursor = db_connection.cursor()
    cursor.execute(
        f"select * from couriers where courier_id = %s;", [courier_id]
    )
    result = cursor.fetchall()[0]
    cursor.close()
    time_intervals = [TimeInterval(e[0] // 60, e[0] % 60, e[1] // 60, e[1] % 60) for e in result[3]]
    return Courier(result[0], CourierType(result[1]), result[2], time_intervals)


# Получить заказ по id
def select_order_by_id(order_id):
    cursor = db_connection.cursor()
    cursor.execute(
        f"select * from orders where order_id = %s;", [order_id]
    )
    result = cursor.fetchall()[0]
    cursor.close()
    time_intervals = [TimeInterval(e[0] // 60, e[0] % 60, e[1] // 60, e[1] % 60) for e in result[3]]
    return Order(result[0], result[1], result[2], time_intervals)


# Обновить информацию о курьере
def update_courier(courier):
    cursor = db_connection.cursor()
    cursor.execute(
        f'update couriers set courier_id = %s, type = %s, regions = %s, working_time = %s where courier_id = %s;',
        [*courier.to_db_entity(), courier.courier_id]
    )
    
    # Также курьер теперь не сможет выполнить некоторые заказы, их нужно освободить
    cursor.execute(
        f'''select * from orders
            where order_id = any(select order_id from assignments where courier_id = %s and completed = false)
                and weight <= %s
                and region = any((select regions from couriers where courier_id = %s)::integer[])
            order by weight;
        ''',
        [courier.courier_id, courier.courier_type.value, courier.courier_id]
    )
    orders_list = cursor.fetchall()

    courier_working_time = prepare_list_of_intervals( [(e.start_time, e.end_time) for e in courier.working_hours] )

    orders_ids = []
    summary_weight = 0
    for e in orders_list:
        # Если курьер уже не может унести на своём хребте заказы, то стоит прекратить ему их назначать
        if summary_weight >= courier.courier_type.value:
            break

        if try_assign_order(courier_working_time, prepare_list_of_intervals(e[3])):
            # Если с новым товаром он сможет утащить
            if summary_weight + e[1] <= courier.courier_type.value:
                summary_weight += e[1] # добавляем вес
                orders_ids.append(e[0]) # сохраняем id заказа, который решили назначить
            else:
                break

    delivery_id = get_not_finished_delivery(courier.courier_id)
    if delivery_id is None:
        return

    if len(orders_ids) == 0:
        if is_completed_any_assignment(delivery_id):
            complete_delivery(delivery_id)
        else:
            delete_delivery(delivery_id)

    cursor.execute(
        f'delete from assignments where courier_id = %s and not order_id = any(%s) and completed = false;',
        [courier.courier_id, orders_ids]
    )
    cursor.close()


# Найти незаконченный развоз курьера
def get_not_finished_delivery(courier_id):
    cursor = db_connection.cursor()
    cursor.execute(
        f'''
        select deliveries.delivery_id from deliveries
        join assignments on deliveries.delivery_id = assignments.delivery_id
        where deliveries.completed = false and assignments.courier_id = %s;
        ''',
        [courier_id]
    )
    delivery_id = cursor.fetchall()
    if len(delivery_id) == 0:
        return None
    return delivery_id[0][0]


# Проверить завершён ли хоть один заказ из развоза. Развоз находится по id курьера и id заказа
def is_completed_any_assignment(delivery_id):
    cursor = db_connection.cursor()
    cursor.execute(
        f'''
        select count(*) from assignments
            where delivery_id = %s
            and completed = true;
        ''',
        [delivery_id]
    )
    result = cursor.fetchall()[0][0]
    cursor.close()

    if result != 0:
        return True
    else:
        return False


# Удалить развоз по id курьера и id заказа
def delete_delivery(delivery_id):
    cursor = db_connection.cursor()
    cursor.execute(
        f'delete from deliveries where delivery_id = %s;',
        [delivery_id]
    )
    cursor.close()


# Проверить, закончил ли курьер развоз
def is_delivery_finished(courier_id):
    cursor = db_connection.cursor()
    cursor.execute(
        f'select count(*) from assignments join deliveries on deliveries.delivery_id = assignments.delivery_id where assignments.courier_id = %s and deliveries.completed = false;',
        [courier_id]
    )
    result = cursor.fetchall()[0][0]
    cursor.close()

    if result == 0:
        return True
    else:
        return False


# Вевнуть список идентификаторов незаконченных товаров
def select_not_finished_assignments(courier_id):
    cursor = db_connection.cursor()
    cursor.execute(
        f'select order_id from assignments where assignments.courier_id = %s and assignments.completed = false;',
        [courier_id]
    )
    result = cursor.fetchall()
    cursor.close()
    return result


# Назначить заказы курьеру
def assign_orders(courier_id, order_ids, assign_time):
    # Если нечего назначить, то и ничего не назначаем
    if len(order_ids) == 0:
        return

    cursor = db_connection.cursor()

    courier = select_courier_by_id(courier_id)
    salary_coefficient = None

    # Рассчитываем кэффициент запрплаты для типа курьера
    if courier.courier_type == CourierType.foot:
        salary_coefficient = 2
    elif courier.courier_type == CourierType.bike:
        salary_coefficient = 5
    else:
        salary_coefficient = 9

    # Создам новый развоз
    cursor.execute(
        f'insert into deliveries (assign_time, completed, salary_coefficient)values (%s, false, %s) returning deliveries.delivery_id;',
        [assign_time, salary_coefficient]
    )
    delivery_id = cursor.fetchall()[0][0]

    # Добавим заказы
    values = [(courier_id, id, delivery_id) for id in order_ids]
    cursor.execute(
        f'insert into assignments (courier_id, order_id, delivery_id) values { ", ".join(["%s"] * len(values)) };',
        values
    )
    cursor.close()


# Проверить назначен ли заказ курьеру
def is_order_assigned_for_courier(courier_id, order_id):
    cursor = db_connection.cursor()
    cursor.execute(
        f'select count(*) from assignments where courier_id = %s and order_id = %s;',
        [courier_id, order_id]
    )
    result = cursor.fetchall()[0][0]
    cursor.close()
    if result == 0:
        return False
    else:
        return True


# Проверить выполнен ли заказ
def is_order_completed(courier_id, order_id):
    cursor = db_connection.cursor()
    cursor.execute(
        f'select count(*) from assignments where courier_id = %s and order_id = %s and completed = false;',
        [courier_id, order_id]
    )
    result = cursor.fetchall()[0][0]
    cursor.close()

    if result == 0:
        return False
    else:
        return True


# Отметить заказ выполненным и по-возможности отметить выполненным развоз
def complete_order(courier_id, order_id, complete_time):
    cursor = db_connection.cursor()
    cursor.execute(
        f'''
        update assignments set completed = true, complete_time = %s, wasted_seconds = extract(epoch from %s) -  extract(epoch from coalesce( 
            (select max(complete_time) from assignments
                join deliveries on assignments.delivery_id = (select delivery_id from assignments where courier_id = %s and order_id = %s)),
            (select assign_time from deliveries
                join assignments on assignments.delivery_id = deliveries.delivery_id
                where assignments.order_id = %s and assignments.courier_id = %s limit 1
            )
            ))
        where courier_id = %s and order_id = %s and completed = false;
        ''',
        [complete_time, complete_time, courier_id, order_id, order_id, courier_id, courier_id, order_id]
    )
    cursor.close()


# Выполнил ли все заказы курьер
def is_completed_all_assignments(courier_id):
    cursor = db_connection.cursor()
    cursor.execute(
        f'select count(*) from assignments where courier_id = %s and completed = false;',
        [courier_id]
    )
    result = cursor.fetchall()[0][0]
    cursor.close()

    if result == 0:
        return True
    else:
        return False


# Отметить развоз, как выполненный
def complete_delivery(delivery_id):
    cursor = db_connection.cursor()
    cursor.execute(
        f'''update deliveries set completed = true
            where deliveries.delivery_id = %s
        ''',
        [delivery_id]
    )
    cursor.close()


# Посчитать заработную плату курьера
def calcuate_courier_sallary(courier_id):
    cursor = db_connection.cursor()
    cursor.execute(
        f'''
            select sum(salary_coefficient)
            from (select deliveries.salary_coefficient, deliveries.delivery_id from deliveries
                join assignments on deliveries.delivery_id = assignments.delivery_id
                where assignments.courier_id = %s and deliveries.completed = true group by deliveries.delivery_id) coeffi;
        ''',
        [courier_id]
    )
    result = cursor.fetchall()[0][0]
    cursor.close()

    if result == None:
        return 0
    else:
        return result * 500


# Рассчитать рейтинг для курьера, возвращает None, если курьер не выполнил ни одного заказа
def get_courier_rating(courier_id):
    cursor = db_connection.cursor()
    cursor.execute(
    f'''
        select min(avg) from
            (select avg(assignments.wasted_seconds), orders.region
                from assignments
                join orders on orders.order_id = assignments.order_id
            where assignments.courier_id = %s and assignments.completed = true group by orders.region)
        avg_regions;
    ''',
    [courier_id]
    )
    result = cursor.fetchall()[0][0]
    cursor.close()
    
    if result == None:
        return None

    # Посчитаю рейтинг и округлю до 2-х чисел после запятой
    rating = (60 * 60 - min(result, 60*60)) / (60*60) * 5
    rating = round(rating, 2)
    return rating


# Перебирает список интервалов и разбивает интервалы, если они проходят через 00:00 на интервалы [x; 23:59] и [00:00; y]
def prepare_list_of_intervals(list_of_tuples):
    for e in list_of_tuples:
        if e[1] < e[0]:
            list_of_tuples.remove(e)
            list_of_tuples.append((e[0], 23 *60 + 59))
            list_of_tuples.append((0, e[1]))
            # Поскольку есть гарантия, что интервалы непересекающиеся, то дальше искать нет смысла
            break
    list_of_tuples.sort(key=lambda x: int(x[0]))
    return list_of_tuples


# Согласно имеющейся у меня информации, заказ назначить можно, если выполняются условя:
# 0) Заказ не назначен другому курьеру
# 1) курьер работает в этом регионе
# 2) вес заказа меньше или равен грузоподъёмности
# 3) есть хотя бы одно ненуливое прересечение интервалов времени доставки заказа и интервалов времени работы курьера
# 4) суммарный вес заказов, выдаваемых курьеру за раз должен быть меньше или равен грузоподъёмности


# Может ли курьер выполнить заказ, временные промежутки должны быть отсортированы,
# а интервалы, проходящие через 00:00, разбиты на [x; 23:59] U [00:00; y]
def try_assign_order(courier_times, delivery_times):

    i = 0 # индекс временных интервалов курьера
    j = 0 # индекс временных интервалов доставки

    while j < len(delivery_times):
        if i == len(courier_times):
            break

        # Если начало работы курьера позже или равно времени конца доставки
        if delivery_times[j][1] <= courier_times[i][0]:
            j += 1
            continue
        # Если курьер работает в то время, когда можно осуществить доставку
        if delivery_times[j][0] < courier_times[i][1]:
            return True
        i += 1
    return False


# Выбрать заказы, вес которых меньше weight и курьер работает в их регионе
def select_orders_for_courier(courier_id):
    courier = select_courier_by_id(courier_id)

    cursor = db_connection.cursor()
    cursor.execute(
        f'''select * from orders
            where weight <= %s
                and region = any((select regions from couriers where courier_id = %s)::integer[])
                and (select count(1) from assignments where orders.order_id = assignments.order_id) = 0
            order by weight;
        ''',
        [courier.courier_type.value, courier_id]
    )
    orders_list = cursor.fetchall()
    cursor.close()

    courier_working_time = prepare_list_of_intervals( [(e.start_time, e.end_time) for e in courier.working_hours] )

    orders_ids = []
    summary_weight = 0
    for e in orders_list:
        # Если курьер уже не может унести на своём хребте заказы, то стоит прекратить ему их назначать
        if summary_weight >= courier.courier_type.value:
            break

        if try_assign_order(courier_working_time, prepare_list_of_intervals(e[3])):
            # Если с новым товаром он сможет утащить
            if summary_weight + e[1] <= courier.courier_type.value:
                summary_weight += e[1] # добавляем вес
                orders_ids.append(e[0]) # сохраняем id заказа, который решили назначить
            else:
                break
    return orders_ids


# Тут будут исключения
db_connection = create_db_connection('candy_shop', 'candy_admin', '1', 'localhost')
db_connection.autocommit = True
init_database(False)


#print(calcuate_courier_sallary(5))