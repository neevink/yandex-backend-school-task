from flask import Flask, jsonify, abort, request
import dal
import services
from models import Courier, CourierType, Order
from exceptions import ValidationException
import json
from json import loads as parse_json, dumps as generate_json
import validator


app = Flask(__name__)


# 1 Import couriers
@app.route('/couriers', strict_slashes = False, methods = ['POST'])
def import_couriers():
    try:
        data = request.data
        d = parse_json(data)['data']
    except:
        return bad_request_with_message_code('По ТЗ такое невозможно, но не удалось спарсить json в теле запроса, возможно отстутствует поле data')

    # Это сообщение первой ошибки валидации
    first_validation_message = None

    success_ids = []
    not_success_ids = []
    new_couriers = []
    for e in d:
        if e.get('courier_id') is None:
            return bad_request_with_message_code('По ТЗ такое невозможно, но у курьера отвутствует поле courier_id типа int')

        # По ТЗ courier_id всегда присутствует, поэтому 
        if len(e) != 4 or e.get('courier_type') is None or e.get('regions') is None or e.get('working_hours') is None:
            not_success_ids.append(e['courier_id'])
            if first_validation_message is None:
                first_validation_message = f'У курьера #{e["courier_id"]} отсутствует обязательное поле или присутствует неописанное'
            continue

        # Если курьер уже содержится в бд, то бракуем его
        if services.is_couriers_contains_id(e['courier_id']):
            not_success_ids.append(e['courier_id'])
            if first_validation_message is None:
                first_validation_message = f'Курьер #{e["courier_id"]} уже содержится в базе данных'
                
        try:
            entity = validator.validate_courier(e)
            new_couriers.append(entity)
            success_ids.append(entity.courier_id)
        except ValidationException as exc:
            not_success_ids.append(e['courier_id'])
            if first_validation_message is None:
                first_validation_message = f'При валидации курьера #{e["courier_id"]} произошла обшибка: ' + str(exc)
    # Отсортарую id и сделаю их уникальными для красоты
    success_ids = list(set(success_ids))
    success_ids.sort()
    not_success_ids = list(set(not_success_ids))
    not_success_ids.sort()
    
    if len(not_success_ids) == 0:      
        try:
            services.add_couriers(new_couriers)
        except:
            return bad_request_with_message_code('Во время выполнения, произошла неожаданная ошибка')
        return created_code(generate_json({'couriers': [{'id':x} for x in success_ids]}))
    else:
        return bad_request_code(generate_json({'validation_error':{'couriers': [{'id':x} for x in not_success_ids], 'first_error_message': first_validation_message}}))


# 2 Update courier by id
@app.route('/couriers/<int:courier_id>', strict_slashes = False, methods = ['PATCH'])
def update_courier_by_id(courier_id):
    try:
        data = request.data
        d = parse_json(data)
    except:
        return bad_request_with_message_code('Не удалось спарсить json в теле запроса')

    try:
        courier = services.get_courier_by_id(courier_id)
    except:
        return not_found_code() # Если передан id курьера, который не существует, то вернуть 404

    # Поля которые могут присутствовать в этом запросе
    accepted_fields = ['courier_type', 'regions', 'working_hours']
    for key in list(d.keys()):
        if key not in accepted_fields:
            return bad_request_with_message_code('В запросе присутствуют неописанные поля')

    if d.get('courier_type') != None:
        try:
            t = validator.validate_type(d.get('courier_type'))
            courier.courier_type = t
        except Exception as e:
            return bad_request_with_message_code('Неверное поле id: ' + str(e))
    
    if d.get('regions') != None:
        try:
            regs = validator.validate_regions(d.get('regions'))
            courier.regions = regs
        except Exception as e:
            return bad_request_with_message_code('Неверное поле regions: ' + str(e))

    if d.get('working_hours') != None:
        try:
            hours = validator.validate_time_list(d.get('working_hours'))
            courier.working_hours = hours
        except Exception as e:
            return bad_request_with_message_code('Неверное поле working_hours: ' + str(e))
    
    try:
        dal.update_courier(courier)
    except:
        return bad_request_with_message_code('Произошла какая-то шибка в базе данных')
    return ok_code(generate_json(courier.to_dict()))


# 3 Import orders
@app.route('/orders', strict_slashes = False, methods = ['POST'])
def import_orders():
    try:
        data = request.data
        d = parse_json(data)['data']
    except:
        return bad_request_with_message_code('Не удалось спарсить json в теле запроса, возможно отстутствует поле data')

    success_ids = []
    not_success_ids = []
    new_orders = []

    for e in d:
        if len(e) != 4 or e.get('order_id') is None or e.get('weight') is None or e.get('region') is None or e.get('delivery_hours') is None:
            return bad_request_with_message_code('В одном из объектов присутствуют неописанные поля и/или отсутствуют обязательные')

        try:
            entity = validator.validate_order(e)
            new_orders.append(entity)
            success_ids.append(entity.order_id)
        except Exception as exc:
            not_success_ids.append(e['order_id'])
    
    if len(not_success_ids) == 0:
        # Если хотя бы один заказ уже содержится в бд, то бракуем весь набор
        if services.is_orders_contains_ids(success_ids):
            return bad_request_with_message_code('Один из заказов с таким id уже существет в базе данных.')

        try:
            services.add_orders(new_orders)
        except:
            return bad_request_with_message_code('Во время выполнения, произошла неожаданная ошибка')
        return created_code(generate_json({"orders": [{"id":x} for x in success_ids]}))
    else:
        return bad_request_code(generate_json({"validation_error":{"orders": [{"id":x} for x in not_success_ids]}}))


# 4 Assign orders to a courier by id
@app.route('/orders/assign', strict_slashes = False, methods = ['POST'])
def assign_orders():
    try:
        data = request.data
        d = parse_json(data)
    except:
        return bad_request_with_message_code('Не удалось спарсить json в теле запроса')
    
    try:
        id = validator.validate_id(d.get('courier_id'))
    except Exception as e:
        return bad_request_with_message_code('Неверное поле courier_id: ' + str(e))

    try:
        result = services.assign_orders(id)
        if type(result) is tuple:
            order_ids = result[0]
            assign_time = result[1].isoformat()[:-4] + 'Z'
            return ok_code(generate_json({"orders": [{"id": x} for x in order_ids], "assign_time": assign_time}))
        else:
            return ok_code(generate_json({"orders": [{"id": x} for x in result]}))
    except:
        return bad_request_with_message_code('Во время выполнения запроса произошла ошибка, скорее всего передан несуществующий id курьера')

    return ok_code(generate_json({"orders": [{"id": x} for x in order_ids], "assign_time": assign_time}))


# 5 Marks orders as completed
@app.route('/orders/complete', strict_slashes = False, methods = ['POST'])
def complete_order():
    try:
        data = request.data
        d = parse_json(data)
    except:
        return bad_request_with_message_code('Не удалось спарсить json в теле запроса')

    try:
        courier_id = validator.validate_id(d.get('courier_id'))
    except Exception as e:
        return bad_request_with_message_code('Неверное поле courier_id: ' + str(e))

    try:
        order_id = validator.validate_id(d.get('order_id'))
    except Exception as e:
        return bad_request_with_message_code('Неверное поле order_id: ' + str(e))
    
    try:
        complete_time = validator.validate_long_time(d.get('complete_time'))
    except Exception as e:
        return bad_request_with_message_code('Неверное поле complete_time: ' + str(e))

    try:
        services.complete_order(courier_id, order_id, complete_time)
    except Exception as e:
        return bad_request_with_message_code(str(e))
    
    return ok_code(generate_json({"order_id": order_id}))


# 6 Get courier info
@app.route('/couriers/<int:courier_id>', strict_slashes = False, methods = ['GET'])
def courier_info(courier_id):
    try:
        courier = services.get_courier_by_id()
    except:
        return not_found_code()

    answer = courier.to_dict()
    rating = services.calculate_courier_rating(courier.courier_id)
    if not rating is None:
        answer['rating'] = rating
    
    answer['earnings'] = services.calcuate_courier_sallary()

    return ok_code(generate_json(answer))


def ok_code(data = ''):
    return data, 200, {'Content-Type': 'application/json; charset=utf-8'}


def created_code(data = ''):
    return data, 201, {'Content-Type': 'application/json; charset=utf-8'}


def bad_request_code(data = ''):
    return data, 400, {'Content-Type': 'application/json; charset=utf-8'}


def bad_request_with_message_code(message):
    return generate_json({'error_message':message}), 400, {'Content-Type': 'application/json; charset=utf-8'}


def not_found_code(data = ''):
    return data, 404, {'Content-Type': 'application/json; charset=utf-8'}


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)