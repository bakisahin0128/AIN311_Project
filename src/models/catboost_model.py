# src/models/catboost_model.py

from catboost import CatBoostClassifier
from .base_model import BaseModel

def get_catboost_model():
    model = CatBoostClassifier(random_state=42, verbose=0)
    param_grid = {
        'iterations': [100, 200, 300],
        'learning_rate': [0.01, 0.1, 0.2],
        'depth': [3, 5, 7],
        'l2_leaf_reg': [1, 3, 5, 7]
    }
    model_name = 'catboost'
    return BaseModel(model, param_grid, model_name)
