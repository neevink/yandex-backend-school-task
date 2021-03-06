from flask import Flask, jsonify, abort
import dal

app = Flask(__name__)

@app.route('/', strict_slashes = False)
def index():
    return '''  <a href="http://localhost:8080/couriers/">/couriers</a>
                <br/>
                <a href="http://localhost:8080/couriers/1">/couriers/1</a>
    '''



@app.route('/couriers', strict_slashes = False, methods = ['GET'])
def get_couriers():
    return jsonify({'data': dal.get_all_couriers()})


@app.route('/couriers/<int:courier_id>', strict_slashes = False, methods = ['GET'])
def get_courier(courier_id):
    entity = dal.get_courier(courier_id)
    if entity == None:
        return abort(404)
    else:
        return jsonify({'data': entity})
    

if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)