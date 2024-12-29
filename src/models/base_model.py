# src/models/base_model.py

from sklearn.model_selection import GridSearchCV
import joblib
import os
import pandas as pd


class BaseModel:
    """
    A base class for machine learning models that handles training with hyperparameter tuning,
    saving the trained model, and saving the best hyperparameters to a CSV file.

    Attributes:
        model: The machine learning model to be trained.
        param_grid (dict): The grid of hyperparameters to search over.
        model_name (str): The name of the model, used for saving files.
        grid_search (GridSearchCV, optional): The GridSearchCV instance after training.
    """

    def __init__(self, model, param_grid, model_name):
        """
        Initializes the BaseModel with a specific machine learning model, its hyperparameter grid,
        and a name for the model.

        Args:
            model: The machine learning model to be trained (e.g., sklearn estimator).
            param_grid (dict): A dictionary specifying the hyperparameter grid for GridSearchCV.
            model_name (str): A name identifier for the model, used in saving files.
        """
        self.model = model
        self.param_grid = param_grid
        self.model_name = model_name
        self.grid_search = None

    def train(self, X_train, y_train):
        """
        Trains the machine learning model using GridSearchCV to find the best hyperparameters.

        Args:
            X_train (pd.DataFrame or np.ndarray): Training feature data.
            y_train (pd.Series or np.ndarray): Training target data.
        """
        self.grid_search = GridSearchCV(
            estimator=self.model,
            param_grid=self.param_grid,
            cv=5,               # 5-fold cross-validation
            n_jobs=-1,          # Utilize all available CPU cores
            verbose=2,          # Verbosity level for logging
            scoring='accuracy'  # Evaluation metric
        )
        self.grid_search.fit(X_train, y_train)
        print(f"Best hyperparameters for {self.model_name}: {self.grid_search.best_params_}")

    def save_model(self):
        """
        Saves the best estimator from GridSearchCV to a pickle file in the 'models' directory.
        """
        models_dir = os.path.join('models')
        os.makedirs(models_dir, exist_ok=True)  # Create 'models' directory if it doesn't exist
        model_path = os.path.join(models_dir, f"{self.model_name}.pkl")
        joblib.dump(self.grid_search.best_estimator_, model_path)
        print(f"{self.model_name} model saved to {model_path}.")

    def save_hyperparameters(self):
        """
        Saves the best hyperparameters found by GridSearchCV to a CSV file in the 'outputs/reports' directory.
        """
        # Retrieve the best hyperparameters
        params = self.grid_search.best_params_
        # Convert the parameters dictionary to a DataFrame
        params_df = pd.DataFrame([params])
        # Define the directory path for saving reports
        reports_dir = os.path.join('outputs', 'reports')
        os.makedirs(reports_dir, exist_ok=True)  # Create 'outputs/reports' directory if it doesn't exist
        # Define the file path for the CSV
        params_csv_path = os.path.join(reports_dir, f"{self.model_name}_best_hyperparameters.csv")
        # Save the DataFrame to CSV
        params_df.to_csv(params_csv_path, index=False)
        print(f"Best hyperparameters saved to {params_csv_path}.")
