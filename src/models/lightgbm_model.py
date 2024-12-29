# src/models/lightgbm_model.py

from lightgbm import LGBMClassifier
from .base_model import BaseModel

def get_lightgbm_model():
    model = LGBMClassifier(random_state=42)
    param_grid = {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7],
        'num_leaves': [31, 50, 100],
        'subsample': [0.7, 0.8, 1.0]
    }
    model_name = 'lightgbm'
    return BaseModel(model, param_grid, model_name)
