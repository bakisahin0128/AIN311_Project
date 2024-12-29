# src/data/load_data.py

import pandas as pd


def load_raw_data(filepath):
    """
    Loads raw data from a CSV file into a pandas DataFrame.

    Args:
        filepath (str): The file path to the CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the loaded raw data.
    """
    try:
        # Load the CSV file into a pandas DataFrame
        df = pd.read_csv(filepath)
        print(f"Data successfully loaded from {filepath}.")
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}. Please check the file path.")
        raise
    except pd.errors.EmptyDataError:
        print(f"Error: The file at {filepath} is empty.")
        raise
    except Exception as e:
        print(f"An unexpected error occurred while loading the data: {e}")
        raise
