def apply_transaction_rules(df):
    '''
    Apply rule-based checks to identify potentially suspicious transactions.
    '''

    # Calculate the 95th percentile of transaction amounts
    amount_threshold = df['Amount'].quantile(0.95)

    # Rule-1: High-value transaction
    df['high_value_flag'] = (
        df['Amount'] >= amount_threshold
    )

    # Rule-2: Late-night transaction
    if "TransactionHour" in df.columns:
        df['late_night_flag'] = (
            (df['TransactionHour'] >= 0) &
            (df['TransactionHour'] <= 5)
        )
    else:
        df['late_night_flag'] = False

    # Rule-3 Risky online transaction
    if "TransactionType" in df.columns:
        online_transaction = (
            df['TransactionType'] == 'Online'
        )

        if "PaymentMethod" in df.columns:
            risky_payment = df['PaymentMethod'].isin(
                ['Credit Card', 'Net Banking']
            )
        else:
            risky_payment = False
        
        df['risky_online_flag'] = (
            online_transaction &
            risky_payment
        )
    else:
        df['risky_online_flag'] = False

    return df