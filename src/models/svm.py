# src/models/svm.py

from sklearn.svm import SVC
from .base_model import BaseModel

def get_svm_model():
    model = SVC(random_state=42)
    param_grid = {
        'C': [0.1, 1, 10, 100],
        'gamma': ['scale', 'auto', 0.001, 0.01, 0.1],
        'kernel': ['linear', 'rbf', 'poly']
    }
    model_name = 'svm'
    return BaseModel(model, param_grid, model_name)
