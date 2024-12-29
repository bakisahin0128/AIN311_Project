# src/models/gradient_boosting.py

from sklearn.ensemble import GradientBoostingClassifier
from .base_model import BaseModel

def get_gradient_boosting_model():
    model = GradientBoostingClassifier(random_state=42)
    param_grid = {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    model_name = 'gradient_boosting'
    return BaseModel(model, param_grid, model_name)
