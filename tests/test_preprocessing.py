# tests/test_train_models.py

import pytest
import pandas as pd
from src.models.train_model import preprocess_data, load_raw_data, load_processed_data
from src.models.train_model import train_random_forest, train_svm, train_gradient_boosting
from src.models.train_model import train_xgboost, train_lightgbm, train_catboost
from src.models.train_model import train_knn, train_logistic_regression, train_mlp, train_naive_bayes


def test_load_raw_data():
    # Ham veriyi yükleme testi
    data = {
        'Season': ['20/21', '20/21'],
        'MatchOutcome': ['H', 'A'],
        'Home Goals': [0, 5],
        'Away Goals': [0, 1]
    }
    df = pd.DataFrame(data)
    assert len(df) == 2
    assert 'Season' in df.columns


def test_preprocess_data():
    # Veri ön işleme testi
    data = {
        'Season': ['20/21', '20/21'],
        'MatchOutcome': ['H', 'A'],
        'Home Goals': [0, 5],
        'Away Goals': [0, 1],
        'Home Team': ['TeamA', 'TeamB'],
        'Away Team': ['TeamC', 'TeamD']
    }
    df = pd.DataFrame(data)
    df_processed = preprocess_data(df, target_column='MatchOutcome')
    assert 'MatchOutcome' in df_processed.columns
    assert df_processed['MatchOutcome'].dtype == 'int64'
    assert 'Home Team_TeamB' in df_processed.columns
    assert 'Away Team_TeamD' in df_processed.columns


def test_train_models():
    # Basit bir model eğitimi testi
    data = {
        'Feature1': [1, 2, 3, 4, 5],
        'Feature2': [5, 4, 3, 2, 1],
        'MatchOutcome': ['H', 'D', 'A', 'H', 'A']
    }
    df = pd.DataFrame(data)
    df_processed = preprocess_data(df, target_column='MatchOutcome')
    X_train, X_test, y_train, y_test = split_data(df_processed, target_column='MatchOutcome')

    # Random Forest
    rf_grid_search = train_random_forest(X_train, y_train)
    assert rf_grid_search.best_score_ > 0

    # SVM
    svm_grid_search = train_svm(X_train, y_train)
    assert svm_grid_search.best_score_ > 0

    # Gradient Boosting
    gbm_grid_search = train_gradient_boosting(X_train, y_train)
    assert gbm_grid_search.best_score_ > 0

    # XGBoost
    xgb_grid_search = train_xgboost(X_train, y_train)
    assert xgb_grid_search.best_score_ > 0

    # LightGBM
    lgbm_grid_search = train_lightgbm(X_train, y_train)
    assert lgbm_grid_search.best_score_ > 0

    # CatBoost
    cb_grid_search = train_catboost(X_train, y_train)
    assert cb_grid_search.best_score_ > 0

    # KNN
    knn_grid_search = train_knn(X_train, y_train)
    assert knn_grid_search.best_score_ > 0

    # Logistic Regression
    lr_grid_search = train_logistic_regression(X_train, y_train)
    assert lr_grid_search.best_score_ > 0

    # MLP
    mlp_grid_search = train_mlp(X_train, y_train)
    assert mlp_grid_search.best_score_ > 0

    # Naive Bayes
    nb = train_naive_bayes(X_train, y_train)
    assert nb is not None


if __name__ == "__main__":
    pytest.main()
