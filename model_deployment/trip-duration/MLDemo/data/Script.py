# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 19:53:40 2017

@author: juan9
"""

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import pickle
import xgboost as xgb
from math import radians, cos, sin, asin, sqrt
import datetime as dt
import json
# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory




# Any results you write to the current directory are saved as output.

train = pd.read_csv("train.csv")
test = pd.read_csv("test.csv")
test_ID = test.id
extra = pd.read_csv("extra.csv",nrows = 1e6)



extra.pickup_datetime = pd.to_datetime(extra.pickup_datetime)
extra.dropoff_datetime = pd.to_datetime(extra.dropoff_datetime)
diff =  (extra.dropoff_datetime - extra.pickup_datetime)
train.pickup_datetime = pd.to_datetime(train.pickup_datetime)
train.dropoff_datetime = pd.to_datetime(train.dropoff_datetime)




extra['trip_duration'] = diff.dt.seconds
del diff
test['trip_duration'] = 0
train = train.append(extra)
train.id = train.id.fillna("id")
del extra
test.pickup_datetime = pd.to_datetime(test.pickup_datetime)
print(train.shape)
train = train.dropna()
train = train.loc[train.passenger_count > 0]
train = train.loc[train.trip_duration > 0]
print(train.shape)
orig_length = len(train)
full = train.append(test)

    


del train
del test
del full["id"]


print("Feature Engineering")
def haversine_array(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(np.radians, (lat1, lng1, lat2, lng2))
    AVG_EARTH_RADIUS = 6371  # in km
    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = np.sin(lat * 0.5) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(lng * 0.5) ** 2
    h = 2 * AVG_EARTH_RADIUS * np.arcsin(np.sqrt(d))
    return h

distances = haversine_array(full['pickup_latitude'].values, full['pickup_longitude'].values, 
            full['dropoff_latitude'].values, full['dropoff_longitude'].values)

full['distance'] = distances
del distances
"""            
def dummy_manhattan_distance(lat1, lng1, lat2, lng2):
    a = haversine_array(lat1, lng1, lat1, lng2)
    b = haversine_array(lat1, lng1, lat2, lng1)
    return a + b

full['mh_distance'] = dummy_manhattan_distance(full['pickup_latitude'].values, full['pickup_longitude'].values,full['dropoff_latitude'].values, full['dropoff_longitude'].values)


#full['distancepp'] = full.distance / full.passenger_count
#full['mhpp'] = full.mh_distance / full.passenger_count


from sklearn.preprocessing import LabelEncoder
vendors = pd.get_dummies(full.vendor_id)
stores = pd.get_dummies(full.store_and_fwd_flag)

full = full.drop("vendor_id", axis = 1)
full = full.drop("store_and_fwd_flag", axis = 1)
vendors.columns = [str(column) for column in vendors.columns]
full['vendor' + (vendors.columns)] = vendors
full['fwdflag' + (stores.columns)] = stores

del vendors
del stores
"""

full.pickup_datetime = pd.to_datetime(full.pickup_datetime)
full['pickuphour'] = full.pickup_datetime.dt.hour
full['pickupweekday'] = full.pickup_datetime.dt.week
full['pickuphourminute'] = full.pickup_datetime.dt.minute
full['pickupmonth'] = full.pickup_datetime.dt.month
full['pickupday'] = full.pickup_datetime.dt.day
full['pickup_dt'] = (full['pickup_datetime'] - full['pickup_datetime'].min()).map(lambda x: x.total_seconds())
full['pickup_date'] = full['pickup_datetime'].dt.date
full.drop("pickup_datetime",axis = 1, inplace = True)




"""
full['direction_ns'] = (full.pickup_latitude>full.dropoff_latitude)*1+1
indices = full[(full.pickup_latitude == full.dropoff_longitude) & (full.pickup_latitude!=0)].index
full.loc[indices,'direction_ns'] = 0

del indices
full['direction_ew'] = (full.pickup_longitude>full.dropoff_longitude)*1+1
indices = full[(full.pickup_longitude == full.dropoff_longitude) & (full.pickup_longitude!=0)].index
full.loc[indices,'direction_ew'] = 0
del indices



full.loc[:, 'center_latitude'] = (full['pickup_latitude'].values + full['dropoff_latitude'].values) / 2
full.loc[:, 'center_longitude'] = (full['pickup_longitude'].values + full['dropoff_longitude'].values) / 2
full.loc[:, 'pickup_lat_bin'] = np.round(full['pickup_latitude'], 3)
full.loc[:, 'pickup_long_bin'] = np.round(full['pickup_longitude'], 3)
full.loc[:, 'center_lat_bin'] = np.round(full['center_latitude'], 3)
full.loc[:, 'center_long_bin'] = np.round(full['center_longitude'], 3)
full.loc[:, 'pickup_dt_bin'] = (full['pickup_dt'] // 10800)


#lgb_full = full.drop(["pickup_date","pickup_dt","mhpp","mh_distance","id","pickup_datetime","pickup_date",
#                     "dropoff_datetime","id"], axis =1)
                     


"""  
lgb_train = full[0:orig_length]
lgb_test = full[orig_length:len(full)]

lgb_train.drop("dropoff_datetime",axis = 1,inplace = True)

test = full[len(lgb_train):len(full)]                  
train = full[0:int(orig_length)]

del lgb_train
del lgb_test


#print(test.shape)
del full
"""
lgb_train.loc[:, 'average_speed_m'] = 1000 * lgb_train['mh_distance'] / lgb_train['trip_duration']
lgb_train.loc[:, 'average_speed_h'] = 1000 * lgb_train['distance'] / lgb_train['trip_duration']

for gby_col in ['pickuphour', 'pickupday', 'pickup_date', 'pickupweekday']:
    print("Mean " + gby_col)
    gby = lgb_train.groupby(gby_col).mean()[['average_speed_h', 'average_speed_m']]
    gby.columns = ['%s_gby_%s' % (col, gby_col) for col in gby.columns]
    lgb_train = pd.merge(lgb_train, gby, how='left', left_on=gby_col, right_index=True)
    lgb_test = pd.merge(lgb_test, gby, how='left', left_on=gby_col, right_index=True)
    del gby
  
lgb_train.trip_duration = np.log(lgb_train.trip_duration)
lgb_train = lgb_train.loc[lgb_train.trip_duration != np.inf]
lgb_y = lgb_train.trip_duration
#lgb_train.drop("trip_duration",axis =1, inplace = True)
#lgb_test.drop("trip_duration",axis = 1, inplace = True)

"""
do_not_use_for_training = ['average_speed_h','average_speed_m','pickup_date', 'trip_duration']


train.trip_duration = np.log(train.trip_duration)
train = train.loc[train.trip_duration != np.inf]
y = train.trip_duration
y_mean = y.mean()

train = train[['distance','pickuphour','pickupweekday']]
test = test[['distance','pickuphour','pickupweekday']]


print("Model training")
np.random.seed(777)
params = {'boosting_type': 'gbdt',
          'max_depth' : -1,
          'objective': 'regression', 
          'nthread': 2, 
          'num_leaves': 98, 
          'learning_rate': 0.01,
          'max_bin': 350, 
          'subsample_for_bin': 170,
          'subsample': 1, 
          'subsample_freq': 1, 
          'colsample_bytree': 0.8, 
          'feature_fraction': 0.9,
          'bagging_fraction':0.95,
          'bagging_freq':5,
          'reg_alpha': 3, 
          'reg_lambda': 5,
          'min_split_gain': 0.5, 
          'min_child_weight': 1, 
          'min_child_samples': 5, 
          'scale_pos_weight': 1,
          'num_class' : 1,
          'metric': 'l2'}

xgb_params = {'min_child_weight': 10, 'eta': 0.01, 'colsample_bytree': 0.5, 'max_depth': 10,
            'subsample': 0.95, 'lambda': 1.,'booster' : 'gbtree', 'silent': 0,
            'eval_metric': 'rmse', 'objective': 'reg:linear'}




params = {}

print("LGB Training")
#Xgbtrain, Xgbtest, Xgbytrain, Xgbytest = train_test_split(train, y, test_size=0.3, random_state=420)
dtrain = xgb.DMatrix(train,y)



model = xgb.XGBRegressor(max_depth=10,learning_rate=0.05,n_estimators=600,subsample=0.95)
model.fit(train,y)

with open('nyc_model.pkl', 'wb') as handle:
    pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)

