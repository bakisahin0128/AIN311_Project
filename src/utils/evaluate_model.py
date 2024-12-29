# src/models/evaluate_model.py

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
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
    print(f"{model_name} model loaded successfully from {model_path}.")
    return model


def evaluate_model(model, X_test, y_test, model_name):
    """
    Evaluates a machine learning model's performance on the test dataset.
    Generates and saves the classification report and confusion matrix.

    Args:
        model: The trained machine learning model to evaluate.
        X_test (pd.DataFrame or np.ndarray): The feature data for testing.
        y_test (pd.Series or np.ndarray): The true labels for testing.
        model_name (str): The name of the model, used for saving reports and figures.
    """
    # Predict the labels for the test set
    y_pred = model.predict(X_test)

    # Generate the classification report
    report = classification_report(y_test, y_pred, output_dict=True)
    report_df = pd.DataFrame(report).transpose()

    # Define the path to save the classification report CSV
    report_path = os.path.join('outputs', 'reports', f"{model_name}_classification_report.csv")
    report_df.to_csv(report_path)
    print(f"Classification report saved to {report_path}.")

    # Calculate the accuracy score
    accuracy = accuracy_score(y_test, y_pred)
    print(f"{model_name} Accuracy Score: {accuracy:.4f}")

    # Generate the confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
    plt.title(f'{model_name} Confusion Matrix')
    plt.xlabel('Predicted Labels')
    plt.ylabel('True Labels')

    # Define the directory path for saving figures
    figures_dir = os.path.join('outputs', 'figures')
    os.makedirs(figures_dir, exist_ok=True)  # Create the directory if it doesn't exist

    # Define the path to save the confusion matrix plot
    cm_path = os.path.join(figures_dir, f"confusion_matrix_{model_name}.png")
    plt.savefig(cm_path)
    plt.close()
    print(f"Confusion matrix plot saved to {cm_path}.")


def evaluate_models(X_test, y_test, model_names):
    """
    Evaluates multiple machine learning models on the test dataset.

    Args:
        X_test (pd.DataFrame or np.ndarray): The feature data for testing.
        y_test (pd.Series or np.ndarray): The true labels for testing.
        model_names (list): A list of model names to evaluate. Each model should have a corresponding '{model_name}.pkl' file in the 'models' directory.
    """
    for model_name in model_names:
        print(f"Evaluating {model_name} model...")
        try:
            # Load the model
            model = load_model(model_name)

            # Evaluate the model
            evaluate_model(model, X_test, y_test, model_name)
            print(f"{model_name} model evaluation completed.\n")
        except FileNotFoundError:
            print(f"Error: Model file for {model_name} not found in the 'models' directory.\n")
        except Exception as e:
            print(f"An error occurred while evaluating the {model_name} model: {e}\n")


