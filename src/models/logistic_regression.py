# src/models/logistic_regression.py

from sklearn.linear_model import LogisticRegression
from .base_model import BaseModel

def get_logistic_regression_model():
    model = LogisticRegression(multi_class='multinomial', solver='lbfgs', random_state=42, max_iter=1000)
    param_grid = {
        'C': [0.01, 0.1, 1, 10, 100],
        'solver': ['lbfgs', 'saga'],
        'penalty': ['l2']
    }
    model_name = 'logistic_regression'
    return BaseModel(model, param_grid, model_name)
