import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_anomalies(df):
    """
    Detect anomalies in the transaction data using Isolation Forest.
    The IsFraud column is excluded because it represents the actual outcome.
    """
    
    # Make a copy so the original DataFrame is not modified unexpectedly
    df = df.copy()

    # Features that can be used for anomaly detection
    numerical_features = [
        "Amount",
        "TransactionHour"
    ]

    categorical_features = [
        "TransactionType",
        "Location",
        "MerchantCategory",
        "PaymentMethod"
    ]

    # Keep only columns that actually exist in the dataset
    numerical_features = [
        col for col in numerical_features
        if col in df.columns
    ]

    categorical_features = [
        col for col in categorical_features
        if col in df.columns
    ]

    # Check whether we have any usable features
    if not numerical_features and not categorical_features:
        df["is_anomaly"] = False
        return df

    # Create a separate DataFrame containing ML features
    features = df[
        numerical_features + categorical_features
    ].copy()

    # Convert numerical columns to numeric values
    for col in numerical_features:
        features[col] = pd.to_numeric(
            features[col],
            errors="coerce"
        )

        # Replace missing values with the median
        features[col] = features[col].fillna(
            features[col].median()
        )
    
    # Replace missing categorical values
    for col in categorical_features:
        features[col] = features[col].fillna("Unknown")
    
    # Convert categorical columns into numerical columns
    features = pd.get_dummies(
        features,
        columns=categorical_features
    )

    # Create the Isolation Forest model
    model = IsolationForest(
        contamination=0.05,
        random_state=42
    )

    try:
        # Train the model and predict anomalies
        predictions = model.fit_predict(features)

        # Isolation Forest:
        # -1 = anomaly
        #  1 = normal
        df["is_anomaly"] = predictions == -1

    except Exception as e:
        print(f"Error in anomaly detection: {e}")
        df["is_anomaly"] = False

    return df