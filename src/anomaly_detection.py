from sklearn.ensemble import IsolationForest

def detect_anomalies(df):
    """
    Detect anomalies in the transaction data using Isolation Forest.
    Assumes that numerical columns can be used for detection.
    Adds a new column 'is_anomaly' to the DataFrame.
    """
    # For this basic version, select numerical features only
    # num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    # Check whether the required transaction feature exists
    if "Amount" not in df.columns:
        df["is_anomaly"] = False
        return df

    # Select only the feature used for anomaly detection
    features = df[["Amount"]]

    # Fit Isolation Forest on the numerical features
    model = IsolationForest(contamination=0.15, random_state=42)
    try:
        # Train the model and predict anomalies
        predictions = model.fit_predict(features)
        # In IsolationForest: -1 = anomaly, 1 = normal
        df['is_anomaly'] = predictions == -1
    except Exception as e:
        print(f"Error in anomaly detection: {e}")
        df['is_anomaly'] = False

    return df
