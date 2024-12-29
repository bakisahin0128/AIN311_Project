# src/models/compare_models.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


def load_classification_report(model_name):
    """
    Loads the classification report from a CSV file and retrieves the accuracy score.

    Parameters:
        model_name (str): The name of the model.

    Returns:
        float: The accuracy score.
    """
    # Construct the path to the classification report CSV file
    report_path = os.path.join('outputs', 'reports', f"{model_name}_classification_report.csv")

    # Read the classification report into a DataFrame, setting the first column as the index
    report_df = pd.read_csv(report_path, index_col=0)

    # Retrieve the 'precision' value from the 'accuracy' row as the accuracy score
    accuracy = report_df.loc['accuracy', 'precision']
    return accuracy


def compare_models():
    """
    Compares the accuracy scores of different models and saves the results to a CSV file.
    Additionally, it visualizes the comparison using a bar plot.
    """
    # List of model names to compare
    models = [
        'random_forest', 'svm',
        'catboost',
        'knn', 'logistic_regression', 'mlp', 'naive_bayes'
    ]
    accuracy = []

    # Iterate over each model to load and collect its accuracy score
    for model in models:
        acc = load_classification_report(model)
        accuracy.append(acc)

    # Create a DataFrame to hold the comparison of models and their accuracy scores
    comparison_df = pd.DataFrame({
        'Model': models,
        'Accuracy': accuracy
    })

    # Define the directory path for saving the comparison CSV
    reports_dir = os.path.join('outputs', 'reports')
    os.makedirs(reports_dir, exist_ok=True)  # Create the directory if it doesn't exist

    # Define the full path for the comparison CSV file
    comparison_csv_path = os.path.join(reports_dir, 'model_accuracy_comparison.csv')

    # Save the comparison DataFrame to a CSV file
    comparison_df.to_csv(comparison_csv_path, index=False)
    print(f"Model accuracy scores saved to {comparison_csv_path}.")

    # Visualization: Create a bar plot comparing the accuracy scores of the models
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Accuracy', y='Model', data=comparison_df, palette='viridis')
    plt.title('Comparison of Model Accuracy Scores')
    plt.xlabel('Accuracy Score')
    plt.ylabel('Models')
    plt.xlim(0, 1)

    # Annotate each bar with its corresponding accuracy score
    for index, row in comparison_df.iterrows():
        plt.text(row['Accuracy'] + 0.005, index, f"{row['Accuracy']:.2f}", va='center')

    # Define the directory path for saving the figures
    figures_dir = os.path.join('outputs', 'figures')
    os.makedirs(figures_dir, exist_ok=True)  # Create the directory if it doesn't exist

    # Save the plot as a PNG file
    plt.savefig(os.path.join(figures_dir, 'model_accuracy_comparison.png'))
    plt.show()
    print("Model accuracy comparison visualization saved.")

