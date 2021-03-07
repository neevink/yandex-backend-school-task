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
        return "", 400

    success = []
    not_success = []

    # Тут ошибка, если в словаре нет courier_id
    for e in d:
        if validator.validate_courier(e) is None:
            not_success.append(e['courier_id'])
        else:
            success.append(e['courier_id'])
    
    if len(not_success) == 0:

        dal.couriers = success
        return json.dumps({"couriers": [{"id":x} for x in success]}), 201
    else:
        return json.dumps({"validation_error":{"couriers": [{"id":x} for x in not_success]}}), 400


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

    hours = validator.validate_hours(d.get('working_hours'))
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
        return "", 400

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
    c = Courier(1, CourierType.foot, [1, 12, 22], ["11:35-14:05", "09:00-11:00"])
    return jsonify({'data': c.to_dict()})


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)


def BadRequst(data):
    return