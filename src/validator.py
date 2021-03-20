from re import match as re_match
from models import CourierType, Courier, Order, TimeInterval
from exceptions import ValidationException
from datetime import datetime


def validate_long_time(element):
    if type(element) != str:
        raise ValidationException('Переданный аргумент имеет неверный тип, ожидается строка')

    t = None
    try:
        t = datetime.strptime(element, '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        raise ValidationException('Cтрока имеет некорректный формат, пример формата: 2021-01-10T09:32:14.42Z')
    return t


def validate_time(element):
    if type(element) != str:
        raise ValidationException("Переданный аргумент имеет неверный тип, ожидается строка")
    
    pattern = r'^([0-1]\d|2[0-3]):[0-5][0-9]-([0-1]\d|2[0-3]):[0-5][0-9]$'
    if re_match(pattern, element) is None:
        raise ValidationException("Cтрока должны быть формата HH:MM-HH:MM")

    start_h = int(element[0:2])
    start_m = int(element[3:5])
    end_h = int(element[6:8])
    end_m = int(element[9:11])

    return TimeInterval(start_h, start_m, end_h, end_m)


def validate_time_list(time_intervals):
    if type(time_intervals) != list:
        raise ValidationException("Переданный аргумент имеет неверный тип, ожидается массив строк")

    try:
        h = list(map(lambda x: validate_time(x), time_intervals))
    except Exception as e:
        raise ValidationException('Недопустимый элемент массива: ' + str(e))
    return h


def validate_regions(regions):
    if type(regions) != list:
        raise ValidationException("Переданный аргумент имеет неверный тип, ожидается массив целых чисел")

    try:
        r = list(map(lambda x: validate_id(x), regions))
    except Exception as e:
        raise ValidationException('Недопустимый элемент массива: ' + str(e))
    return r


def validate_id(element):
    if type(element) == int:
        if element > 0:
            return element
        else:
            raise ValidationException("Переданный аргумент должен быть положительным числом (больше нуля)")
    else:
        raise ValidationException("Переданный аргумент имеет неверный тип, ожидается целое число")


def validate_type(element):
    if element == 'foot':
        return CourierType.foot
    elif element == 'bike':
        return CourierType.bike
    elif element == 'car':
        return CourierType.car
    else:
        raise ValidationException("Переданный аргумент должен иметь одно из значений перечисления CourierType")


def validate_weight(weight):
    if type(weight) != float and type(weight) != int:
        raise ValidationException("Переданный аргумент имеет неверный тип, ожидается число")
    if weight < 0.01 or weight > 50:
        raise ValidationException("Вес не может быть меньше 0.01 и больше 50")
    else:
        return float(weight)


def validate_courier(courier_dict):
    try:
        id = validate_id(courier_dict.get('courier_id'))
    except Exception as e:
        raise ValidationException('Поле courier_id - ' + str(e))

    try:
        t = validate_type(courier_dict.get('courier_type'))
    except Exception as e:
        raise ValidationException('Поле courier_type - ' + str(e))
    
    try:
        regions = validate_regions(courier_dict.get('regions'))
    except Exception as e:
        raise ValidationException('Поле regions - ' + str(e))

    try:
        hours = validate_time_list(courier_dict.get('working_hours'))
    except Exception as e:
        raise ValidationException('Поле working_hours - ' + str(e))
    
    return Courier(id, t, regions, hours)


def validate_order(order_dict):
    id = validate_id(order_dict.get('order_id'))
    w = validate_weight(order_dict.get('weight'))
    reg = validate_id(order_dict.get('region'))
    hours = validate_time_list(order_dict.get('delivery_hours'))

    return Order(id, w, reg, hours)
