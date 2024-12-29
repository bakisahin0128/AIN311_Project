# src/pipeline/run_pipeline.py

import os
import pandas as pd
from src.utils.load_data import load_raw_data
from src.utils.preprocess import preprocess_data
from src.models.random_forest import get_random_forest_model
from src.models.svm import get_svm_model
from src.models.gradient_boosting import get_gradient_boosting_model
from src.models.xgboost_model import get_xgboost_model
from src.models.lightgbm_model import get_lightgbm_model
from src.models.catboost_model import get_catboost_model
from src.models.knn import get_knn_model
from src.models.logistic_regression import get_logistic_regression_model
from src.models.mlp import get_mlp_model
from src.models.naive_bayes import get_naive_bayes_model
from src.utils.evaluate_model import evaluate_models
from src.utils.compare_models import compare_models
from src.utils.feature_importance import feature_importance_analysis
from sklearn.model_selection import train_test_split


def run_pipeline():
    """
    Executes the machine learning pipeline, which includes data loading, preprocessing,
    model training with hyperparameter tuning, evaluation, comparison, and feature importance analysis.
    """
    # 1. Data Loading
    raw_data_path = r"/data/processed/final\all_seasons_final.csv"
    df_raw = load_raw_data(raw_data_path)
    print("Raw data loaded successfully.")

    # 2. Data Preprocessing
    df_processed = preprocess_data(df_raw, target_column='MatchOutcome')
    processed_data_path = r"/data/processed/final\cleaned.csv"
    df_processed.to_csv(processed_data_path, index=False)
    print("Data preprocessing completed and saved.")

    # 3. Data Splitting
    X = df_processed.drop('MatchOutcome', axis=1)
    y = df_processed['MatchOutcome']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("Data split into training and testing sets.")

    # 4. Model Definition
    models = [
        get_random_forest_model(),
        get_svm_model(),
        get_catboost_model(),
        get_knn_model(),
        get_logistic_regression_model(),
        get_mlp_model(),
        get_naive_bayes_model(),
    ]
    print("Models have been defined.")

    # 5. Model Training and Saving
    for model in models:
        print(f"Training {model.model_name} model...")
        model.train(X_train, y_train)
        model.save_model()
        model.save_hyperparameters()
        print(f"{model.model_name} model trained and saved.\n")

    # 6. Model Evaluation
    print("Evaluating models...")
    model_names = [model.model_name for model in models]
    evaluate_models(X_test, y_test, model_names)
    print("Model evaluation completed.")

    # 7. Model Comparison
    print("Comparing models...")
    compare_models()
    print("Model comparison completed.")

    # 8. Feature Importance Analysis
    print("Performing feature importance analysis...")
    feature_importance_analysis()
    print("Feature importance analysis completed.")

