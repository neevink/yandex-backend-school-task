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
        # Если отсутствует id курьера, но это не ошибка валидации, а плохой запрос
        if e.get('courier_id') is None:
            return bad_request_with_message_code('У одного из элементов отсутствует поле courier_id')
        
        try:
            entity = validator.validate_courier(e)
            new_couriers.append(entity)
            success_ids.append(entity.courier_id)
        except:
            not_success_ids.append(e['courier_id'])
            
    if len(not_success_ids) == 0:
        services.add_couriers(new_couriers)
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

    courier = services.get_courier_by_id(courier_id)
    # Если передан id курьера, который не существует, то вернуть 404
    if courier is None:
        return not_found_code()

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
            return bad_request_with_message_code('Неверное поле working_hours: ' + e)

    dal.update_courier(courier)
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
        # Если отсутствует id заказа, но это не ошибка валидации, а плохой запрос
        if e.get('order_id') is None:
            return bad_request_with_message_code('У одного из элементов отсутствует поле order_id')

        try:
            entity = validator.validate_order(e)
            new_orders.append(entity)
            success_ids.append(entity.order_id)
        except Exception as exc:
            not_success_ids.append(e['order_id'])
    
    if len(not_success_ids) == 0:
        services.add_orders(new_orders)
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
    
    if d.get('courier_id') != None:
        try:
            id = validator.validate_int(d.get('courier_id'))
        except Exception as e:
            return bad_request_with_message_code('Неверное поле courier_id: ' + e)

    # Тут какой-нибудь алгос...
    order_ids = services.select_orders_for_courier(id)

    return ok_code(json.dumps({"orders": [{"id": x} for x in order_ids]}))


# 5
@app.route('/orders/complete', strict_slashes = False, methods = ['POST'])
def complete_order():
    try:
        data = request.data
        d = json.loads(data)
    except:
        return "", 400

    order_id = validator.validate_int(d.get('order_id'))
    if order_id is None:
        return "", 400
    
    courier_id = validator.validate_int(d.get('courier_id'))
    if courier_id is None:
        return "", 400
    
    # Тут метод который там ты понял
    return json.dumps({"order_id": order_id}), 200

# 6
@app.route('/couriers/<int:courier_id>', strict_slashes = False, methods = ['GET'])
def courier_info(courier_id):
    # Тут тоже запросик, вытащить
    c = Courier(1, CourierType.car, [2, 3], ['12:00-13:00']).to_dict()
    c['rating'] = 3.4
    c['earnings'] = 10000

    return json.dumps(c), 200


@app.route('/', strict_slashes = False, methods = ['GET'])
def get_couriers():
    m = list(map(lambda x: x.to_dict(), dal.couriers))
    o = list(map(lambda x: x.to_dict(), dal.orders))
    return jsonify({'couriers': m, 'orders': o})


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