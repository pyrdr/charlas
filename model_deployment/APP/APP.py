from flask import Flask, request
from flask import render_template
from flask import jsonify
from dataprep import prepare_data
from predict import predict_price
from helpers import conseguir_historial, conseguir_scores
import datetime
from babel.numbers import format_currency


app = Flask(__name__)
app.config['DEBUG'] = True

tipo_vivienda_map = {"apartamento": "apartamentos", "casa": "casas", "villas": "casas vacacionales y villas",
                     "vivienda compartida": "habitaciones y viviendas compartidas",
                     "local": "oficinas y locales comerciales",
                     "solar": "solares y terrenos", "penthouse": "penthouses"}


def prepare_params(params):
    print(params)
    params_dict = {}
    tipo_vivienda = tipo_vivienda_map[params.get('tipo').lower()]
    params_dict[tipo_vivienda] = 1
    params_dict['numero_hab'] = int(params.get('numero_hab'))
    params_dict['numero_banios'] = int(params.get('numero_ban'))
    params_dict['construccion'] = int(params.get('area_cons'))
    params_dict['Solar'] = int(params.get('area_solar'))
    params_dict['Sector'] = params.get('sector').lower()
    municipio = params.get('municipio').lower()
    params_dict[municipio] = 1
    params_dict['Lat'] = float(params.get('lat'))
    params_dict['Long'] = float(params.get('lng'))
    today = datetime.date.today()
    params_dict['Anio'] = today.year
    params_dict['Mes'] = today.month
    return params_dict


@app.route('/', defaults={'path': ''})
def hello_world(path):
    return render_template('build/index.html')


@app.route('/api')
def controller():
    tipo_request = request.args.get('tipo_request')
    json_response = None
    if tipo_request == 'price':
        json_response = get_price_prediction(request)
    elif tipo_request == 'historial_predicciones':
        json_response = get_historial_cambio_predicciones()
    elif tipo_request == 'historial_scores':
        json_response = get_historial_cambio_scores()

    return jsonify(json_response)


def get_price_prediction(request):
    params_dict = prepare_params(request.args)
    prepared_data = prepare_data(params_dict)
    low_prediction, high_prediction, explicacion_dict, explicacion_text = predict_price(prepared_data,
                                                                                        params_dict['Sector'])
    json_response = {
        'precio_low': format_currency(int(low_prediction), 'USD', locale='en_US'),
        'precio_high': format_currency(int(high_prediction), 'USD', locale='en_US'),
        'explicacion_data': explicacion_dict,
        'explicacion_text': explicacion_text
    }
    print(json_response)
    return json_response


def get_historial_cambio_predicciones():
    cambio_historial = conseguir_historial()
    cambio_dict = {"cambios": cambio_historial}
    return cambio_dict


def get_historial_cambio_scores():
    cambio_scores = conseguir_scores()
    cambio_dict = {"scores": cambio_scores}
    print(cambio_dict)
    return cambio_dict


if __name__ == '__main__':
    app.run(debug=True,
            host='127.0.0.1',
            port=9000,
            threaded=True)
