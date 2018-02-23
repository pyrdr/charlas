from sklearn.externals import joblib
import unicodedata
from nltk.stem.snowball import SpanishStemmer
import re
import nltk
from sklearn.externals import joblib
import pandas as pd
import os
import json
import urllib

spanish_stops = set(nltk.corpus.stopwords.words('Spanish'))
stemmer = SpanishStemmer()

path = os.path.dirname(os.path.abspath(__file__)) + "\\"

def _assign_geo_cluster(lat_long):

    geo_cluster_model = joblib.load(path + 'geo_cluster_model.pkl')

    cluster = geo_cluster_model.predict(lat_long)[0]
    return cluster



def _strip_accents(s):
    #Reemplaza las letras con tilde por su equivalente sin tilde.
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def Clean_Text(text):
    # Limpia strings.

    words = text.lower().split()  # LLeva todo a minuscula y divide en palabras.
    removed_stops = [stemmer.stem(w) for w in words if not w in spanish_stops]
    no_accents = _strip_accents(" ".join(removed_stops))  # Reemplaza tildes.
    letters_only = re.sub("[^a-zA-Z]", " ", no_accents)  # Elimina caracteres no alfabeticos.
    no_one_letter = [w for w in letters_only.split() if len(w) != 1]

    return " ".join(no_one_letter)  # Unirlo todo a una oración nuevamente.


def Get_Text_Vectors(data,text_col="Descripcion"):
    count_vectorizer = joblib.load(path + 'count_vectorizer.pkl')
    try:
        docterm_matrix = count_vectorizer.fit_transform(list(data[text_col]))
    except ValueError:
        return data


    data= pd.concat([data, pd.DataFrame(docterm_matrix.todense(),
                                                                 columns=count_vectorizer.get_feature_names())], axis=1)

    tf_vectorizer = joblib.load(path + 'tf_vectorizer.pkl')
    tf_idf_matrix = tf_vectorizer.fit_transform(list(data[text_col]))

    data = pd.concat([data, pd.DataFrame(tf_idf_matrix.todense(),
                                                                 columns=["{}-tf-idf".format(name)
                                                                          for name in
                                                                          tf_vectorizer.get_feature_names()])], axis=1)

    return data

import math
def Calcular_Distancia(lat1,long1,lat2,long2):
    lat1, lng1, lat2, lng2 = map(math.radians, (lat1, long1, lat2, long2))
    AVG_EARTH_RADIUS = 6371  # in km
    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = math.sin(lat * 0.5) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(lng * 0.5) ** 2
    h = 2 * AVG_EARTH_RADIUS * math.asin(math.sqrt(d))
    return h

def Get_Nearby_Data(data,lat_long):
    print(lat_long)
    base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=LAT,LONG&radius=1500&key=AIzaSyAidCqawUm8KobiTyLIszZPaM0TB8tuPK8'
    url = base_url.replace('LAT', str(lat_long[0])).replace('LONG', str(lat_long[1]))
    page = json.loads(urllib.request.urlopen(url).read())
    for r in page['results']:
        for t in r['types']:
            data[t] = 1
            lat_long_near = r['geometry']['location']
            distancia = Calcular_Distancia(lat_long_near['lat'], lat_long_near['lng'], lat_long[0], lat_long[1])
            data["Distancia {}".format(t)] = distancia

    print(data)
    return data




def prepare_data(params_dict):
    data = pd.DataFrame(params_dict,index=[0])
    data['Geo_Cluster'] = _assign_geo_cluster(data[["Lat","Long"]])
    data = Get_Nearby_Data(data,data[["Lat","Long"]].values[0])
    data[data["Sector"].values[0]] = 1
    data.drop(["Sector"],axis=1,inplace=True)
    return data



