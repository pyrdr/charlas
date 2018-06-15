from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os
import numpy as np
import pandas as pd
import math
import datetime
import xgboost as xgb

def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
list_files(BASE_DIR)
file_dir = BASE_DIR + "/MLDemo/data/"
model = xgb.Booster({'nthread':-1})
model.load_model(file_dir + 'nyc_model.model')

IntecLatitude = 18.481779
IntecLongitude = -69.956399

# Create your views here.



def Calcular_Distancia(lat,long):
    lat1, lng1, lat2, lng2 = map(math.radians, (lat, long, IntecLatitude, IntecLongitude))
    AVG_EARTH_RADIUS = 6371  # in km
    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = math.sin(lat * 0.5) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(lng * 0.5) ** 2
    h = 2 * AVG_EARTH_RADIUS * math.asin(math.sqrt(d))
    return h


def Home(request):
    test = {'distance':400,'pickuphour':18,'pickupweekday':6}
    test = pd.DataFrame(test,index=[0])
    print(model)
    t = model.predict(xgb.DMatrix(test))
    print(np.exp(t) / 60)
    return render(request, 'Home.html')

@csrf_exempt
def duration(request):
    print(request.POST)
    Latitud = request.POST.get('latitud')
    Longitud = request.POST.get('longitud')
    Hora = request.POST.get('hora')
    print(Latitud)
    print(Longitud)
    Distancia = Calcular_Distancia(float(Latitud),float(Longitud))
    Dia = datetime.datetime.now().weekday()


    test_data = pd.DataFrame({'distance':Distancia
                                 ,'pickuphour':int(Hora)
                                 ,'pickupweekday':Dia},index = [0])

    prediction = np.exp(model.predict(xgb.DMatrix(test_data)))/60

    json = {'prediction':str(math.ceil(prediction[0]))}
    print(prediction)
    print(json)
    return JsonResponse(json,safe=False)



