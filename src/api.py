from flask import Flask, jsonify, abort, request
import dal
import services
from models import Courier, CourierType, Order
import json
from json import loads as parse_json, dumps as generate_json
import validator


app = Flask(__name__)


# 1
@app.route('/couriers', strict_slashes = False, methods = ['POST'])
def import_couriers():
    try:
        data = request.data
        d = parse_json(data)['data']
    except:
        return bad_request_with_message_code('Не удалось спарсить json в теле запроса, возможно отстутствует поле data')

    success_ids = []
    not_success_ids = []
    new_couriers = []
    for e in d:
        if len(e) != 4 or e.get('courier_id') is None or e.get('courier_type') is None or e.get('regions') is None or e.get('working_hours') is None:
            return bad_request_with_message_code('В одном из объектов присутствуют неописанные поля и/или отсутствуют обязательные')
                
        try:
            entity = validator.validate_courier(e)
            new_couriers.append(entity)
            success_ids.append(entity.courier_id)
        except:
            not_success_ids.append(e['courier_id'])
            
    if len(not_success_ids) == 0:
        # Если хотя бы один курьер уже содержится в бд, то бракуем весь набор
        if services.is_couriers_contains_ids(success_ids):
            return bad_request_with_message_code('Один из курьеров с таким id уже существет в базе данных.')
        
        try:
            services.add_couriers(new_couriers)
        except:
            return bad_request_with_message_code('Во время выполнения, произошла неожаданная ошибка')
        return created_code(generate_json({"couriers": [{"id":x} for x in success_ids]}))
    else:
        return bad_request_code(generate_json({"validation_error":{"couriers": [{"id":x} for x in not_success_ids]}}))


# 2
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


# 3
@app.route('/orders', strict_slashes = False, methods = ['POST'])
def import_orders():
    try:
        data = request.data
        d = json.loads(data)['data']
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
        return created_code(json.dumps({"orders": [{"id":x} for x in success_ids]}))
    else:
        return bad_request_code(json.dumps({"validation_error":{"orders": [{"id":x} for x in not_success_ids]}}))


# 4
@app.route('/orders/assign', strict_slashes = False, methods = ['POST'])
def assign_orders():
    try:
        data = request.data
        d = json.loads(data)
    except:
        return bad_request_with_message_code('Не удалось спарсить json в теле запроса')
    
    try:
        id = validator.validate_int(d.get('courier_id'))
    except Exception as e:
        return bad_request_with_message_code('Неверное поле courier_id: ' + str(e))

    try:
        result = services.assign_orders(id)
        if type(result) is tuple:
            order_ids = result[0]
            assign_time = result[1].isoformat()[:-4] + 'Z'
            return ok_code(json.dumps({"orders": [{"id": x} for x in order_ids], "assign_time": assign_time}))
        else:
            return ok_code(json.dumps({"orders": [{"id": x} for x in result]}))
    except:
        return bad_request_with_message_code('Во время выполнения запроса произошла ошибка, скорее всего передан несуществующий id курьера')

    return ok_code(json.dumps({"orders": [{"id": x} for x in order_ids], "assign_time": assign_time}))


# 5
@app.route('/orders/complete', strict_slashes = False, methods = ['POST'])
def complete_order():
    try:
        data = request.data
        d = json.loads(data)
    except:
        return bad_request_with_message_code('Не удалось спарсить json в теле запроса')

    try:
        courier_id = validator.validate_int(d.get('courier_id'))
    except Exception as e:
        return bad_request_with_message_code('Неверное поле courier_id: ' + str(e))

    try:
        order_id = validator.validate_int(d.get('order_id'))
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
    
    return ok_code(json.dumps({"order_id": order_id}))

# 6
@app.route('/couriers/<int:courier_id>', strict_slashes = False, methods = ['GET'])
def courier_info(courier_id):
    # Тут тоже запросик, вытащить
    c = Courier(1, CourierType.car, [2, 3], ['12:00-13:00']).to_dict()
    c['rating'] = 3.4
    c['earnings'] = 10000

    return ok_code(json.dumps(c))


def ok_code(data = ''):
    return data, 200


def created_code(data = ''):
    return data, 201


def bad_request_code(data = ''):
    return data, 400


def bad_request_with_message_code(message):
    return generate_json({'error_message':message}), 400


def not_found_code(data = ''):
    return data, 404


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)