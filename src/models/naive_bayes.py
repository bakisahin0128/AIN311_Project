# src/models/naive_bayes.py

from sklearn.naive_bayes import GaussianNB
from .base_model import BaseModel

def get_naive_bayes_model():
    model = GaussianNB()
    param_grid = {
        # GaussianNB için hiperparametreler sınırlıdır
        # Örneğin, priors gibi
        'priors': [None]  # Varsayılan olarak sınıf oranları kullanılır
    }
    model_name = 'naive_bayes'
    return BaseModel(model, param_grid, model_name)
