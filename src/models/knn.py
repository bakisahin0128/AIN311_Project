# src/models/knn.py

from sklearn.neighbors import KNeighborsClassifier
from .base_model import BaseModel

def get_knn_model():
    model = KNeighborsClassifier()
    param_grid = {
        'n_neighbors': [3, 5, 7, 9],
        'weights': ['uniform', 'distance'],
        'metric': ['euclidean', 'manhattan']
    }
    model_name = 'knn'
    return BaseModel(model, param_grid, model_name)
