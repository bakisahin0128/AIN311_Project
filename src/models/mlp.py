# src/models/mlp.py

from sklearn.neural_network import MLPClassifier
from .base_model import BaseModel

def get_mlp_model():
    model = MLPClassifier(random_state=42, max_iter=500)
    param_grid = {
        'hidden_layer_sizes': [(50,), (100,), (100, 50)],
        'activation': ['relu', 'tanh'],
        'solver': ['adam', 'sgd'],
        'alpha': [0.0001, 0.001, 0.01],
        'learning_rate': ['constant', 'adaptive']
    }
    model_name = 'mlp'
    return BaseModel(model, param_grid, model_name)
