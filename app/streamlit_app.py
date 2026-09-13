import sys
import os
import pandas as pd
import streamlit as st

# -------------------------
# Fix import path for custom modules
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
sys.path.insert(0, SRC_DIR)

# -------------------------
# Set page configuration as the first Streamlit command
st.set_page_config(
    page_title="Suspicious Transaction Monitoring",
    layout="wide"
)

# -------------------------
# Import our custom modules
from anomaly_detection import detect_anomalies
from utils import load_data
from transaction_rules import apply_transaction_rules
from risk_scoring import calculate_risk_score

# -------------------------
# Custom CSS
st.markdown("""
    <style>
    body {
        background-color: #f0f2f6;
    }

    h1, h2, h3, h4 {
        color: #333333;
    }

    .stMarkdown p {
        font-size: 16px;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------
# Initialize session state
if "proceed" not in st.session_state:
    st.session_state.proceed = False

if "filters_applied" not in st.session_state:
    st.session_state.filters_applied = False

# -------------------------
# About Section
if not st.session_state.proceed:

    st.title(
        "🔍 Suspicious Transaction Monitoring & Anomaly Detection"
    )

    st.markdown("""
    ## About This Tool

    This tool analyzes financial transaction data to identify
    potentially suspicious and unusual transaction patterns.

    **Key Features:**

    - **Transaction Monitoring:** Analyze transactions for unusual activity.
    - **Anomaly Detection:** Use machine learning to identify transactions
      that differ significantly from normal transaction patterns.
    - **Rule-Based Monitoring:** Apply transaction monitoring rules
      such as high-value and late-night transaction checks.
    - **Risk Scoring:** Combine machine learning and rule-based signals
      to assign a risk score and risk level.
    - **Data Flexibility:** Use sample data or upload your own CSV file.
    - **Dynamic Filtering & Sorting:** Filter and sort transactions.
    - **Detailed Transaction View:** Inspect individual transactions.
    - **Fraud Evaluation:** Compare anomaly detection with actual fraud
      labels when available.

    This tool supports transaction monitoring and risk analysis.

    An anomaly does not necessarily indicate confirmed fraud and
    should be reviewed further.
    """)

    st.markdown("---")

# -------------------------
# Sidebar: Data Source Selection
st.sidebar.subheader("📁 Data Source Selection")

data_option = st.sidebar.radio(
    "Select Data Source",
    options=["Use Sample Data", "Upload CSV File"]
)

uploaded_file = None

if data_option == "Upload CSV File":

    uploaded_file = st.sidebar.file_uploader(
        "Upload your transaction CSV",
        type=["csv"]
    )

# -------------------------
# Proceed Button
if data_option == "Use Sample Data" or (
    data_option == "Upload CSV File"
    and uploaded_file is not None
):

    if st.sidebar.button("Proceed"):
        st.session_state.proceed = True

else:

    st.sidebar.info(
        "Please upload your CSV file to proceed."
    )

# -------------------------
# Process Data
if st.session_state.proceed:

    # -------------------------
    # Load uploaded data
    if data_option == "Upload CSV File":

        if uploaded_file is not None:

            df = pd.read_csv(uploaded_file)

            st.sidebar.success(
                "✅ File uploaded successfully!"
            )

        else:

            st.warning(
                "⚠️ Please upload a CSV file to proceed."
            )

            st.stop()

    # -------------------------
    # Load sample data
    else:

        sample_path = os.path.join(
            ROOT_DIR,
            "data",
            "transactions.csv"
        )

        df = load_data(sample_path)

        st.sidebar.info(
            "💡 Using sample transactions.csv"
        )

    # -------------------------
    # Check whether data was loaded
    if df.empty:

        st.error(
            "❌ No data loaded. Please check your CSV file."
        )

        st.stop()

    # -------------------------
    # Check Amount column
    if "Amount" not in df.columns:

        st.error(
            "❌ The dataset must contain an 'Amount' column."
        )

        st.stop()

    # -------------------------
    # Detect anomalies
    if "is_anomaly" not in df.columns:

        df = detect_anomalies(df)

    # -------------------------
    # Apply transaction monitoring rules
    if "high_value_flag" not in df.columns:

        df = apply_transaction_rules(df)

    # -------------------------
    # Calculate risk score
    if "risk_level" not in df.columns:

        df = calculate_risk_score(df)

    # -------------------------
    # Sidebar Filters
    st.sidebar.subheader(
        "🔍 Filter & Sort Transactions"
    )

    min_amt = st.sidebar.number_input(
        "Minimum Amount",
        min_value=0.0,
        value=float(df["Amount"].min())
    )

    max_amt = st.sidebar.number_input(
        "Maximum Amount",
        min_value=0.0,
        value=float(df["Amount"].max())
    )

    show_anomalies_only = st.sidebar.checkbox(
        "Show Anomalies Only",
        value=False
    )

    show_suspicious_only = st.sidebar.checkbox(
        "Show Suspicious Only",
        value=False
    )

    if st.sidebar.button("Apply Filters"):

        st.session_state.filters_applied = True

    # -------------------------
    # Apply Filters
    if st.session_state.filters_applied:

        filtered_df = df[
            (df["Amount"] >= min_amt) &
            (df["Amount"] <= max_amt)
        ]

        # ML anomaly filter
        if show_anomalies_only:

            filtered_df = filtered_df[
                filtered_df["is_anomaly"] == True
            ]

        # Risk-based filter
        if show_suspicious_only:

            filtered_df = filtered_df[
                filtered_df["risk_level"] != "Low"
            ]

        # -------------------------
        # Sort Data
        if not filtered_df.empty:

            sort_column = st.sidebar.selectbox(
                "Sort By",
                options=filtered_df.columns,
                index=filtered_df.columns.get_loc("Amount")
                if "Amount" in filtered_df.columns
                else 0
            )

            sort_order = st.sidebar.radio(
                "Sort Order",
                options=["Ascending", "Descending"]
            )

            filtered_df = filtered_df.sort_values(
                by=sort_column,
                ascending=(sort_order == "Ascending")
            )

        else:

            st.sidebar.warning(
                "No data matches the filter criteria."
            )

        # -------------------------
        # Risk Summary Metrics
        total_transactions = len(filtered_df)

        suspicious_transactions = (
            filtered_df["risk_level"] != "Low"
        ).sum()

        high_risk_transactions = (
            filtered_df["risk_level"] == "High"
        ).sum()

        medium_risk_transactions = (
            filtered_df["risk_level"] == "Medium"
        ).sum()

        # -------------------------
        # Dashboard Metrics
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Transactions",
            total_transactions
        )

        col2.metric(
            "Suspicious Transactions",
            suspicious_transactions
        )

        col3.metric(
            "High Risk",
            high_risk_transactions
        )

        col4.metric(
            "Medium Risk",
            medium_risk_transactions
        )


        # -------------------------
        # Suspicious Transactions
        suspicious_df = filtered_df[
            filtered_df["risk_level"] != "Low"
        ]

        st.subheader(
            "🚨 Suspicious Transactions"
        )

        if not suspicious_df.empty:

            display_columns = [
                "TransactionID",
                "Amount",
                "TransactionType",
                "Location",
                "MerchantCategory",
                "PaymentMethod",
                "TransactionHour",
                "is_anomaly",
                "high_value_flag",
                "late_night_flag",
                "risky_online_flag",
                "risk_score",
                "risk_level"
            ]

            # Display only columns that exist
            display_columns = [
                col for col in display_columns
                if col in suspicious_df.columns
            ]

            st.dataframe(
                suspicious_df[display_columns],
                use_container_width=True
            )

        else:

            st.success(
                "No suspicious transactions found."
            )

        # -------------------------
        # Display Filtered Data
        st.subheader(
            "📋 Filtered Transaction Data"
        )

        st.dataframe(
            filtered_df,
            use_container_width=True
        )

        # -------------------------
        # Detailed Transaction View
        st.subheader(
            "🔎 Detailed Transaction View"
        )

        if not filtered_df.empty:

            transaction_ids = (

                filtered_df["TransactionID"].astype(str)

                if "TransactionID" in filtered_df.columns

                else filtered_df.index.astype(str)
            )

            selected_id = st.selectbox(
                "Select Transaction ID",
                options=transaction_ids
            )

            # Find selected transaction
            if "TransactionID" in filtered_df.columns:

                selected_row = filtered_df[
                    filtered_df["TransactionID"].astype(str)
                    == selected_id
                ]

            else:

                selected_row = filtered_df.loc[
                    [int(selected_id)]
                ]

            st.markdown(
                "**Transaction Details:**"
            )

            st.json(
                selected_row.to_dict(
                    orient="records"
                )[0]
            )

        else:

            st.info(
                "No transactions available for detailed view."
            )

    else:

        st.info(
            "Please adjust filters and click "
            "**Apply Filters** to update the results."
        )

else:

    st.info(
        "Please select a data source and click "
        "**Proceed** from the sidebar to begin processing."
    )

