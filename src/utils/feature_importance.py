# src/models/feature_importance.py

import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os


def load_model(model_name):
    """
    Loads a trained machine learning model from a pickle file.

    Args:
        model_name (str): The name of the model to load. The corresponding file should be named '{model_name}.pkl'.

    Returns:
        model: The loaded machine learning model.
    """
    # Construct the path to the model's pickle file
    model_path = os.path.join('models', f"{model_name}.pkl")

    # Load the model using joblib
    model = joblib.load(model_path)
    print(f"{model_name} model loaded successfully.")
    return model


def load_processed_data(filepath):
    """
    Loads the processed data from a CSV file.

    Args:
        filepath (str): The path to the processed CSV file.

    Returns:
        pd.DataFrame: The loaded DataFrame containing processed data.
    """
    df = pd.read_csv(filepath)
    return df


def plot_feature_importance(model, model_name, X_columns, top_n=10):
    """
    Visualizes the top N most important features of a given model.

    Depending on the model type, it handles feature importance differently.

    Parameters:
        model: The trained machine learning model.
        model_name (str): The name of the model.
        X_columns (list): List of feature names.
        top_n (int): Number of top features to display.
    """
    if model_name in ['random_forest', 'gradient_boosting', 'xgboost', 'lightgbm', 'catboost']:
        # Extract feature importances from tree-based models
        importances = model.feature_importances_
        feature_importance = pd.Series(importances, index=X_columns)
        top_features = feature_importance.sort_values(ascending=False).head(top_n)

        # Plotting the feature importances
        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_features.values, y=top_features.index, palette='magma')
        plt.title(f'{model_name.replace("_", " ").title()} Top {top_n} Important Features')
        plt.xlabel('Feature Importance')
        plt.ylabel('Feature')

        # Ensure the figures directory exists
        figures_dir = os.path.join('outputs', 'figures')
        os.makedirs(figures_dir, exist_ok=True)

        # Save the plot
        plt.savefig(os.path.join(figures_dir, f"{model_name}_feature_importance.png"))
        plt.close()
        print(f"{model_name} feature importance plot saved to {figures_dir}.")

    elif model_name == 'logistic_regression':
        # Extract coefficients from logistic regression
        coefficients = model.coef_[0]
        feature_importance = pd.Series(coefficients, index=X_columns)
        top_features = feature_importance.abs().sort_values(ascending=False).head(top_n)

        # Plotting the feature coefficients
        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_features.values, y=top_features.index, palette='coolwarm')
        plt.title(f'{model_name.replace("_", " ").title()} Top {top_n} Feature Contributions')
        plt.xlabel('Feature Coefficient')
        plt.ylabel('Feature')

        # Ensure the figures directory exists
        figures_dir = os.path.join('outputs', 'figures')
        os.makedirs(figures_dir, exist_ok=True)

        # Save the plot
        plt.savefig(os.path.join(figures_dir, f"{model_name}_feature_importance.png"))
        plt.close()
        print(f"{model_name} feature coefficient plot saved to {figures_dir}.")

    elif model_name == 'svm':
        # For SVMs that have coefficients (linear SVM)
        if hasattr(model, 'coef_'):
            coefficients = model.coef_[0]
            feature_importance = pd.Series(coefficients, index=X_columns)
            top_features = feature_importance.abs().sort_values(ascending=False).head(top_n)

            # Plotting the feature coefficients
            plt.figure(figsize=(10, 6))
            sns.barplot(x=top_features.values, y=top_features.index, palette='coolwarm')
            plt.title(f'{model_name.upper()} Top {top_n} Important Features')
            plt.xlabel('Feature Coefficient')
            plt.ylabel('Feature')

            # Ensure the figures directory exists
            figures_dir = os.path.join('outputs', 'figures')
            os.makedirs(figures_dir, exist_ok=True)

            # Save the plot
            plt.savefig(os.path.join(figures_dir, f"{model_name}_feature_importance.png"))
            plt.close()
            print(f"{model_name} feature coefficient plot saved to {figures_dir}.")
        else:
            print(f"{model_name} does not have a direct feature importance attribute.")

    else:
        print(f"No direct feature importance available for {model_name}.")


def feature_importance_analysis():
    """
    Performs feature importance analysis for multiple models and visualizes the top features.
    """
    # Define the path to the processed data
    processed_data_path = os.path.join('data', 'processed', 'cleaned_data.csv')

    # Load the processed data
    df = load_processed_data(processed_data_path)

    # Get the feature names by excluding the target column
    X_columns = df.drop('MatchOutcome', axis=1).columns.tolist()

    # List of models to analyze
    models = [
        'random_forest', 'svm',
        'catboost',
        'knn', 'logistic_regression', 'mlp', 'naive_bayes'
    ]

    for model_name in models:
        # Only perform feature importance analysis for models that support it
        if model_name in ['random_forest', 'catboost',
                          'logistic_regression', 'svm']:
            try:
                # Load the trained model
                model = load_model(model_name)

                # Plot and save feature importance
                plot_feature_importance(model, model_name, X_columns, top_n=10)
            except FileNotFoundError:
                print(f"Model file for {model_name} not found in the 'models' directory.")
            except Exception as e:
                print(f"An error occurred while analyzing feature importance for {model_name}: {e}")
        else:
            print(f"Feature importance analysis not performed for {model_name}.")

