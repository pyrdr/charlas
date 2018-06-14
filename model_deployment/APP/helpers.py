import pandas as pd
import numpy as np
import os
import  json

def conseguir_historial():
    path = os.path.dirname(os.path.abspath(__file__)) + "\\"
    history = pd.read_csv(path + "Predicciones_History.csv")
    predicciones_cols = [col for col in history.columns if 'Pred' in col]
    history = history.loc[pd.notnull(history[predicciones_cols[0]])]
    diferencias_dict = []
    for i in range(len(predicciones_cols) - 1):
        dif_fecha = dict()
        dif_fecha["Fecha"] = predicciones_cols[i].replace("Predicciones_2018-", "")
        dif_fecha["Diferencia"] = np.abs((history[predicciones_cols[i]] - history[predicciones_cols[i + 1]]).mean())
        diferencias_dict.append(dif_fecha)

    diferencias_dict.reverse()
    return diferencias_dict


def conseguir_scores():
    path = os.path.dirname(os.path.abspath(__file__)) + "\\"
    scores = json.loads(open(path + "scores_date.json",'r').read())

    return scores