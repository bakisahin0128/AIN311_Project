# src/data/preprocess.py

import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler


def remove_duplicate_columns(df):
    """
    Removes duplicate columns from the DataFrame.

    Args:
        df (pd.DataFrame): Original DataFrame.

    Returns:
        pd.DataFrame: DataFrame with duplicate columns removed.
    """
    df = df.loc[:, ~df.columns.duplicated()]
    return df


def drop_columns(df, columns_to_drop):
    """
    Drops specified columns from the DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame.
        columns_to_drop (list): List of column names to drop.

    Returns:
        pd.DataFrame: DataFrame with specified columns removed.
    """
    missing_columns = [col for col in columns_to_drop if col not in df.columns]
    if missing_columns:
        print(f"Warning: The following columns were not found in the DataFrame and were not dropped: {missing_columns}")
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors='ignore')
    return df


def handle_missing_values(df):
    """
    Fills missing values in the DataFrame.

    Numerical columns are filled with their median, and categorical columns are filled with their mode.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: DataFrame with missing values handled.
    """
    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    df[numerical_cols] = df[numerical_cols].fillna(df[numerical_cols].median())
    df[categorical_cols] = df[categorical_cols].fillna(df[categorical_cols].mode().iloc[0])

    return df


def encode_categorical_features(df, columns_to_encode):
    """
    Encodes specified categorical columns using Label Encoding.

    Args:
        df (pd.DataFrame): Input DataFrame.
        columns_to_encode (list): List of column names to encode.

    Returns:
        pd.DataFrame: DataFrame with encoded categorical features.
    """
    le = LabelEncoder()
    for column in columns_to_encode:
        if column in df.columns:
            df[column] = le.fit_transform(df[column])
        else:
            print(f"Warning: Column '{column}' was not found in the DataFrame.")
    return df


def scale_numerical_features(df, target_column, exclude_columns=None):
    """
    Scales numerical features in the DataFrame, excluding specified columns.

    Args:
        df (pd.DataFrame): Input DataFrame.
        target_column (str): Name of the target variable column.
        exclude_columns (list, optional): List of columns to exclude from scaling.

    Returns:
        pd.DataFrame: DataFrame with scaled numerical features.
    """
    scaler = StandardScaler()
    numerical_features = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    # Exclude the target column and specified columns from scaling
    columns_to_exclude = [target_column]
    if exclude_columns:
        columns_to_exclude.extend(exclude_columns)

    numerical_features = [col for col in numerical_features if col not in columns_to_exclude]

    df[numerical_features] = scaler.fit_transform(df[numerical_features])

    return df


def encode_target_variable(df, target_column):
    """
    Encodes the target variable into numerical format.

    Args:
        df (pd.DataFrame): Input DataFrame.
        target_column (str): Name of the target variable column.

    Returns:
        pd.DataFrame: DataFrame with the target variable encoded.
    """
    df[target_column] = df[target_column].map({'H': 0, 'D': 1, 'A': 2})
    return df


def preprocess_data(df, target_column='MatchOutcome'):
    """
    Performs a sequence of preprocessing steps on the input DataFrame.

    Steps include:
    1. Removing duplicate columns.
    2. Dropping specified columns.
    3. Handling missing values.
    4. Encoding categorical features.
    5. Encoding the target variable.
    6. Scaling numerical features.

    Args:
        df (pd.DataFrame): Original DataFrame.
        target_column (str): Name of the target variable column.

    Returns:
        pd.DataFrame: Preprocessed DataFrame.
    """
    # Step 1: Remove duplicate columns
    df = remove_duplicate_columns(df)

    # Step 2: Drop unwanted columns
    columns_to_drop = ['Season', 'Season.1', 'Week', 'Match Date', 'Match Date.1', 'Home Goals', 'Away Goals', 'Home Performance', 'Away Performance']
    df = drop_columns(df, columns_to_drop)

    # Step 3: Handle missing values
    df = handle_missing_values(df)

    # Step 4: Scale numerical features, excluding 'Home_Advantage'
    df = scale_numerical_features(df, target_column, exclude_columns=['Home_Advantage'])

    # Step 5: Encode specified categorical columns
    columns_to_encode = ['Home Team', 'Away Team', 'Home Formation', 'Away Formation']
    df = encode_categorical_features(df, columns_to_encode)

    # Step 6: Encode the target variable
    df = encode_target_variable(df, target_column)

    return df
