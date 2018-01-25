# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 20:56:56 2018

@author: Dario
"""
#%%
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import norm, skew
from sklearn.preprocessing import LabelEncoder
from scipy.special import boxcox1p
from sklearn.base import BaseEstimator, TransformerMixin
#%%
class ThenTransformer(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        X.drop("Id", axis = 1, inplace = True)
        # Eliminamos los outliers
        X = X.drop(X[(X['GrLivArea']>4000) & (X['SalePrice']<300000)].index)
        # Eliminamos la variable a predecir
        X.drop(['SalePrice'], axis=1, inplace=True)
        #
        X["PoolQC"] = X["PoolQC"].fillna("None")
        #
        X["MiscFeature"] = X["MiscFeature"].fillna("None")
        X["Alley"] = X["Alley"].fillna("None")
        X["Fence"] = X["Fence"].fillna("None")
        X["FireplaceQu"] = X["FireplaceQu"].fillna("None")
        #
        for col in ('GarageType', 'GarageFinish', 'GarageQual', 'GarageCond'):
            X[col] = X[col].fillna('None')
        # 
        # Agrupamos por vecindario y completamos los valores perdidos con la mediana de LotFrontage para todos los vecindarios
        X["LotFrontage"] = X.groupby("Neighborhood")["LotFrontage"].transform(
            lambda x: x.fillna(x.median()))
        #
        for col in ('GarageYrBlt', 'GarageArea', 'GarageCars'):
            X[col] = X[col].fillna(0)
        #    
        for col in ('BsmtFinSF1', 'BsmtFinSF2', 'BsmtUnfSF','TotalBsmtSF', 'BsmtFullBath', 'BsmtHalfBath'):
            X[col] = X[col].fillna(0)
        #
        for col in ('BsmtQual', 'BsmtCond', 'BsmtExposure', 'BsmtFinType1', 'BsmtFinType2'):
            X[col] = X[col].fillna('None')
        #
        X["MasVnrType"] = X["MasVnrType"].fillna("None")
        X["MasVnrArea"] = X["MasVnrArea"].fillna(0)
        #
        X['MSZoning'] = X['MSZoning'].fillna(X['MSZoning'].mode()[0])
        X = X.drop(['Utilities'], axis=1)
        X["Functional"] = X["Functional"].fillna("Typ")
        X['Electrical'] = X['Electrical'].fillna(X['Electrical'].mode()[0])
        X['KitchenQual'] = X['KitchenQual'].fillna(X['KitchenQual'].mode()[0])
        X['Exterior1st'] = X['Exterior1st'].fillna(X['Exterior1st'].mode()[0])
        X['Exterior2nd'] = X['Exterior2nd'].fillna(X['Exterior2nd'].mode()[0])
        X['SaleType'] = X['SaleType'].fillna(X['SaleType'].mode()[0])
        X['MSSubClass'] = X['MSSubClass'].fillna("None")
        #
        # MSSubClass = El tipo de edificios
        X['MSSubClass'] = X['MSSubClass'].apply(str)
        # OverallCond
        X['OverallCond'] = X['OverallCond'].astype(str)
        # Año y mes de venta.
        X['YrSold'] = X['YrSold'].astype(str)
        X['MoSold'] = X['MoSold'].astype(str)
        #
        cols = ('FireplaceQu', 'BsmtQual', 'BsmtCond', 'GarageQual', 'GarageCond', 
                'ExterQual', 'ExterCond','HeatingQC', 'PoolQC', 'KitchenQual', 'BsmtFinType1', 
                'BsmtFinType2', 'Functional', 'Fence', 'BsmtExposure', 'GarageFinish', 'LandSlope',
                'LotShape', 'PavedDrive', 'Street', 'Alley', 'CentralAir', 'MSSubClass', 'OverallCond', 
                'YrSold', 'MoSold')
        # procesa columnas, applicando LabelEncoder a los atributos categóricos
        for c in cols:
            lbl = LabelEncoder() 
            lbl.fit(list(X[c].values)) 
            X[c] = lbl.transform(list(X[c].values))
        #
        # Adicionamos el total de pies cuadrados (TotalSF) de la vivienda
        X['TotalSF'] = X['TotalBsmtSF'] + X['1stFlrSF'] + X['2ndFlrSF']
        #
        numeric_feats = X.dtypes[X.dtypes != "object"].index
        # Verificamos el sesgo de todos los atributos numéricos
        skewed_feats = X[numeric_feats].apply(lambda x: skew(x.dropna())).sort_values(ascending=False)
        skewness = pd.DataFrame({'Skew' :skewed_feats})
        #
        skewness = skewness[abs(skewness) > 0.75]
        skewed_features = skewness.index
        lam = 0.15
        for feat in skewed_features:
            X[feat] = boxcox1p(X[feat], lam)
        #
        X = pd.get_dummies(X)
        #
        return X