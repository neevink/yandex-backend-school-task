from flask import Flask, jsonify, abort, request
import dal
from models import Courier, CourierType, Order
import json
import validator


app = Flask(__name__)


# 1
@app.route('/couriers', strict_slashes = False, methods = ['POST'])
def import_couriers():
    try:
        data = request.data
        d = json.loads(data)['data']
    except:
        return bad_request_code()

    success_ids = []
    not_success_ids = []
    new_couriers = []
    for e in d:
        # Если отсутствует id курьера, но это не ошибка валидации, а плохой запрос
        if e.get('courier_id') is None:
            return bad_request_code()
        
        try:
            entity = validator.validate_courier(e)
            new_couriers.append(entity)
            success_ids.append(entity.courier_id)
        except:
            not_success_ids.append(e['courier_id'])
            
    if len(not_success_ids) == 0:
        dal.add_couriers(new_couriers)
        return created_code(json.dumps({"couriers": [{"id":x} for x in success_ids]}))
    else:
        return bad_request_code(json.dumps({"validation_error":{"couriers": [{"id":x} for x in not_success_ids]}}))


# 2
@app.route('/couriers/<int:courier_id>', strict_slashes = False, methods = ['PATCH'])
def update_courier_by_id(courier_id):
    try:
        data = request.data
        d = json.loads(data)
    except:
        return "", 400

    t = validator.validate_type(d.get('courier_type'))
    if d.get('courier_type') != None and t == None:
        return "", 400

    regs = validator.validate_regions(d.get('regions'))
    if d.get('regions') != None and regs == None:
        return "", 400

    hours = validator.validate_time_list(d.get('working_hours'))
    if d.get('working_hours') != None and hours == None:
        return "", 400

    # Тут проблемка, он не изменяет объект, а возвращает переданные данные
    c = Courier(courier_id, t, regs, hours).to_dict()
    return json.dumps(c), 200


# 3
@app.route('/orders', strict_slashes = False, methods = ['POST'])
def import_orders():
    try:
        data = request.data
        d = json.loads(data)['data']
    except:
        return bad_request_code()

    success = []
    not_success = []

    # Тут ошибка, если в словаре нет order_id
    for e in d:
        if validator.validate_order(e) is None:
            not_success.append(e['order_id'])
        else:
            success.append(e['order_id'])
    
    if len(not_success) == 0:
        # Тут вызов метода dal.add order
        return json.dumps({"orders": [{"id":x} for x in success]}), 201
    else:
        return json.dumps({"validation_error":{"orders": [{"id":x} for x in not_success]}}), 400


# 4
@app.route('/orders/assign', strict_slashes = False, methods = ['POST'])
def assign_orders():
    try:
        data = request.data
        d = json.loads(data)
    except:
        return "", 400

    courier_id = validator.validate_int(d.get('courier_id'))
    if courier_id is None:
        return "", 400

    # Тут какой-нибудь алгос...
    order_ids = [1, 2, 3]

    return json.dumps({"orders": [{"id": x} for x in order_ids]}), 200


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
    return jsonify({'data': m})


def ok_code(data = ''):
    return data, 200


def created_code(data = ''):
    return data, 201


def bad_request_code(data = ''):
    return data, 400


def not_found_code(data = ''):
    return data, 404


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)