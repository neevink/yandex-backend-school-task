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
@app.route('/couriers', strict_slashes=False, methods=['POST'])
def import_couriers():
    try:
        data = request.data
        d = parse_json(data)['data']
    except Exception:
        return bad_request_with_message_code(
            'По ТЗ такое невозможно, но не удалось спарсить json в теле '
            'запроса, возможно отстутствует поле data')

    # Это сообщение первой ошибки валидации
    first_validation_message = None

    success_ids = []
    not_success_ids = []
    new_couriers = []
    for e in d:
        if e.get('courier_id') is None:
            return bad_request_with_message_code(
                'По ТЗ такое невозможно, но у курьера отвутствует '
                'поле courier_id')

        # По ТЗ courier_id всегда присутствует, поэтому
        if len(e) != 4 or e.get('courier_type') is None or e.get('regions') \
                is None or e.get('working_hours') is None:
            not_success_ids.append(e['courier_id'])
            if first_validation_message is None:
                first_validation_message = (f'У курьера #{e["courier_id"]} '
                                            'отсутствует обязательное поле '
                                            'или присутствует неописанное')
            continue

        # Если курьер уже содержится в бд, то бракуем его
        if services.is_couriers_contains_id(e['courier_id']):
            not_success_ids.append(e['courier_id'])
            if first_validation_message is None:
                first_validation_message = (f'Курьер #{e["courier_id"]} уже '
                                            'содержится в базе данных')

        try:
            entity = validator.validate_courier(e)
            new_couriers.append(entity)
            success_ids.append(entity.courier_id)
        except ValidationException as exc:
            not_success_ids.append(e['courier_id'])
            if first_validation_message is None:
                first_validation_message = ('При валидации курьера '
                                            f'#{e["courier_id"]} '
                                            'произошла обшибка: ' + str(exc))
    # Отсортарую id и сделаю их уникальными для красоты
    success_ids = list(set(success_ids))
    success_ids.sort()
    not_success_ids = list(set(not_success_ids))
    not_success_ids.sort()

    if len(not_success_ids) == 0:
        try:
            services.add_couriers(new_couriers)
        except Exception:
            return bad_request_with_message_code('Во время выполнения,'
                                                 'произошла ошибка: cкорее '
                                                 'всего в запросе дублируются '
                                                 'courier_id (по ТЗ такого '
                                                 'быть не должно)')
        ans = generate_json({'couriers': [{'id': x} for x in success_ids]})
        return created_code(ans)
    else:
        ans = generate_json({
            'validation_error': {
                'couriers': [{'id': x} for x in not_success_ids],
                'first_error_message': first_validation_message}
        })
        return bad_request_code(ans)


# 2 Update courier by id
@app.route(
    '/couriers/<int:courier_id>',
    strict_slashes=False,
    methods=['PATCH'])
def update_courier_by_id(courier_id):
    try:
        data = request.data
        d = parse_json(data)
    except Exception:
        return bad_request_with_message_code(
            'Не удалось спарсить json в теле запроса')

    try:
        courier = services.get_courier_by_id(courier_id)
    except Exception:
        return not_found_code()  # Если курьер не существует, то вернуть 404

    # Поля которые могут присутствовать в этом запросе
    accepted_fields = ['courier_type', 'regions', 'working_hours']
    for key in list(d.keys()):
        if key not in accepted_fields:
            return bad_request_with_message_code(
                'В запросе присутствуют неописанные поля')

    if d.get('courier_type') is not None:
        try:
            t = validator.validate_type(d.get('courier_type'))
            courier.courier_type = t
        except Exception as e:
            return bad_request_with_message_code(
                'Неверное поле courier_type: ' + str(e))

    if d.get('regions') is not None:
        try:
            regs = validator.validate_regions(d.get('regions'))
            courier.regions = regs
        except Exception as e:
            return bad_request_with_message_code(
                'Неверное поле regions: ' + str(e))

    if d.get('working_hours') is not None:
        try:
            hours = validator.validate_time_list(d.get('working_hours'))
            courier.working_hours = hours
        except Exception as e:
            return bad_request_with_message_code(
                'Неверное поле working_hours: ' + str(e))

    try:
        dal.update_courier(courier)
    except Exception:
        return bad_request_with_message_code(
            'Произошла какая-то шибка в базе данных')

    return ok_code(generate_json(courier.to_dict()))


# 3 Import orders
@app.route('/orders', strict_slashes=False, methods=['POST'])
def import_orders():
    try:
        data = request.data
        d = parse_json(data)['data']
    except Exception:
        return bad_request_with_message_code(
            'По ТЗ такое невозможно, но не удалось спарсить json в теле '
            'запроса, возможно отстутствует поле data')

    # Это сообщение первой ошибки валидации
    first_validation_message = None

    success_ids = []
    not_success_ids = []
    new_orders = []
    for e in d:
        if e.get('order_id') is None:
            return bad_request_with_message_code(
                'По ТЗ такое невозможно, но у заказа отвутствует '
                'поле order_id')

        if len(e) != 4 or e.get('order_id') is None \
                or e.get('weight') is None \
                or e.get('region') is None \
                or e.get('delivery_hours') is None:
            not_success_ids.append(e['order_id'])
            if first_validation_message is None:
                first_validation_message = (f'У заказа  # {e["order_id"]} '
                                            'отсутствует обязательное поле '
                                            'или присутствует неописанное')
            continue

        # Если заказ уже содержится в бд, то бракуем его
        if services.is_orders_contains_id(e['order_id']):
            not_success_ids.append(e['order_id'])
            if first_validation_message is None:
                first_validation_message = (f'Заказ #{e["order_id"]} уже '
                                            'содержится в базе данных')

        try:
            entity = validator.validate_order(e)
            new_orders.append(entity)
            success_ids.append(entity.order_id)
        except Exception as exc:
            not_success_ids.append(e['order_id'])
            if first_validation_message is None:
                first_validation_message = ('При валидации заказа '
                                            f'#{e["order_id"]} произошла '
                                            'обшибка: ' + str(exc))
    # Отсортарую id и сделаю их уникальными
    success_ids = list(set(success_ids))
    success_ids.sort()
    not_success_ids = list(set(not_success_ids))
    not_success_ids.sort()

    if len(not_success_ids) == 0:
        try:
            services.add_orders(new_orders)
        except Exception:
            return bad_request_with_message_code(
                'Во время выполнения, произошла ошибка: '
                'cкорее всего в запросе дублируются '
                'order_id (по ТЗ такого быть не должно)')

        ans = generate_json({'orders': [{'id': x} for x in success_ids]})
        return created_code(ans)
    else:
        ans = generate_json({
            'validation_error': {
                'orders': [{'id': x} for x in not_success_ids],
                'first_error_message': first_validation_message
                }
            })
        return bad_request_code(ans)


# 4 Assign orders to a courier by id
@app.route('/orders/assign', strict_slashes=False, methods=['POST'])
def assign_orders():
    try:
        data = request.data
        d = parse_json(data)
    except Exception:
        return bad_request_with_message_code(
            'По ТЗ такое невозможно, но не удалось спарсить '
            'json в теле запроса')

    if len(d) != 1 or d.get('courier_id') is None:
        return bad_request_code()

    try:
        id = validator.validate_id(d.get('courier_id'))
        # Проверим, существует ли курьер
        services.get_courier_by_id(d.get('courier_id'))
    except Exception:
        return bad_request_code()

    try:
        result = services.assign_orders(id)
        if type(result) is tuple:
            order_ids = result[0]
            assign_time = result[1].isoformat()[:-4] + 'Z'
            ans = generate_json({
                "orders": [{"id": x} for x in order_ids],
                "assign_time": assign_time
                })
            return ok_code(ans)
        else:
            ans = generate_json({"orders": [{"id": x} for x in result]})
            return ok_code(ans)
    except Exception:
        return bad_request_with_message_code(
            'Во время выполнения запроса произошла ошибка.')


# 5 Marks orders as completed
@app.route('/orders/complete', strict_slashes=False, methods=['POST'])
def complete_order():
    try:
        data = request.data
        d = parse_json(data)
    except Exception:
        return bad_request_with_message_code(
            'По ТЗ такое невозможно, но не удалось спарсить '
            'json в теле запроса')

    if len(d) != 3 or d.get('courier_id') is None or \
            d.get('order_id') is None or d.get('complete_time') is None:
        return bad_request_code()

    try:
        courier_id = validator.validate_id(d.get('courier_id'))
    except Exception:
        return bad_request_code()

    try:
        order_id = validator.validate_id(d.get('order_id'))
    except Exception:
        return bad_request_code()

    try:
        complete_time = validator.validate_long_time(d.get('complete_time'))
    except Exception:
        return bad_request_code()

    try:
        services.complete_order(courier_id, order_id, complete_time)
    except Exception:
        return bad_request_code()

    return ok_code(generate_json({"order_id": order_id}))


# 6 Get courier info
@app.route('/couriers/<int:courier_id>', strict_slashes=False, methods=['GET'])
def courier_info(courier_id):
    try:
        courier = services.get_courier_by_id(courier_id)
    except Exception:
        return not_found_code()

    answer = courier.to_dict()
    rating = services.calculate_courier_rating(courier_id)
    if rating is not None:
        answer['rating'] = rating

    answer['earnings'] = services.calcuate_courier_sallary(courier_id)

    return ok_code(generate_json(answer))


def ok_code(data=''):
    return data, 200, {'Content-Type': 'application/json; charset=utf-8'}


def created_code(data=''):
    return data, 201, {'Content-Type': 'application/json; charset=utf-8'}


def bad_request_code(data=''):
    return data, 400, {'Content-Type': 'application/json; charset=utf-8'}


def bad_request_with_message_code(message):
    body = generate_json({'error_message': message})
    return body, 400, {'Content-Type': 'application/json; charset=utf-8'}


def not_found_code(data=''):
    return data, 404, {'Content-Type': 'application/json; charset=utf-8'}


# Встроенный возвращает HTML, да ещё и текст, нужно это убрать
@app.errorhandler(404)
def not_found(error):
    return '', 404, {'Content-Type': 'application/json; charset=utf-8'}


@app.errorhandler(400)
def not_found(error):
    return '', 400, {'Content-Type': 'application/json; charset=utf-8'}


if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)
