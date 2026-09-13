def calculate_risk_score(df):
    '''
    Combine ML anomaly detection and rule-based monitoring to assign a risk score and risk level.
    '''

    # Start every transaction with a score of 0
    df['risk_score'] = 0

    # ML anomaly
    df.loc[df['is_anomaly'], 'risk_score'] += 40

    # High-value transaction
    df.loc[df['high_value_flag'], 'risk_score'] += 25

    # Late-night transaction
    df.loc[df["late_night_flag"], "risk_score"] += 15

    # Risky online transaction
    df.loc[df["risky_online_flag"], "risk_score"] += 20

    # Convert the score into a risk category
    df['risk_level'] = 'Low'

    # Medium risk: 30-59
    df.loc[
        (df['risk_score'] >= 30) &
        (df['risk_score'] < 60),
        'risk_level'
    ] = 'Medium'

    # High risk: 60-100
    df.loc[
        (df['risk_score'] >= 60) &
        (df['risk_score'] <= 100),
        'risk_level'
    ] = 'High'

    return df