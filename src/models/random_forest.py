# src/models/random_forest.py

from sklearn.ensemble import RandomForestClassifier
from .base_model import BaseModel

def get_random_forest_model():
    model = RandomForestClassifier(random_state=42)
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'bootstrap': [True, False]
    }
    model_name = 'random_forest'
    return BaseModel(model, param_grid, model_name)
