# src/models/xgboost_model.py

from xgboost import XGBClassifier
from .base_model import BaseModel

def get_xgboost_model():
    model = XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='mlogloss')
    param_grid = {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7],
        'subsample': [0.7, 0.8, 1.0],
        'colsample_bytree': [0.7, 0.8, 1.0]
    }
    model_name = 'xgboost'
    return BaseModel(model, param_grid, model_name)
