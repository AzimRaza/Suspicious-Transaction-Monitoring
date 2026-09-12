import sys
import os
import pandas as pd
import streamlit as st
from fpdf import FPDF

# -------------------------
# Fix import path for custom modules
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
sys.path.insert(0, SRC_DIR)

# -------------------------
# Set page configuration as the first Streamlit command
st.set_page_config(page_title="AI-Based Fraud Detector", layout="wide")

# -------------------------
# Import our custom modules
from anomaly_detection import detect_anomalies
from utils import load_data

# -------------------------
# Inject custom CSS for a modern look
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
    .loading-spinner {
        font-style: italic;
        color: #555;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------
# Initialize session state for processing control
if 'proceed' not in st.session_state:
    st.session_state.proceed = False

if 'filters_applied' not in st.session_state:
    st.session_state.filters_applied = False

# -------------------------
# Detailed About Section
if not st.session_state.proceed:
    st.title("💰 AI-Based Financial Fraud Detector")
    st.markdown("""
    ## About This Tool

    This tool analyzes financial transactions and detects unusual
    activity that may indicate potential fraud.

    **Key Features:**
    - **Automated Fraud Detection:** Uses anomaly detection techniques
      to flag unusual transactions.
    - **Data Flexibility:** Use sample data or upload your own CSV file.
    - **Dynamic Filtering & Sorting:** Filter transactions by amount,
      date, and anomaly status.
    - **Detailed Transaction View:** Select a transaction to inspect
      its details.
    - **Interactive Analysis:** Explore suspicious transactions and
      identify potentially unusual activity.

    This tool is designed for quick transaction analysis and
    fraud-risk identification.
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

if data_option == "Use Sample Data" or (
    data_option == "Upload CSV File" and uploaded_file is not None
):
    if st.sidebar.button("Proceed"):
        st.session_state.proceed = True
else:
    st.sidebar.info("Please upload your CSV file to proceed.")

# -------------------------
# Process Data Only After User Proceeds
if st.session_state.proceed:

    if data_option == "Upload CSV File":

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.sidebar.success("✅ File uploaded successfully!")
        else:
            st.warning("⚠️ Please upload a CSV file to proceed.")
            st.stop()

    else:
        sample_path = os.path.join(
            ROOT_DIR,
            "data",
            "transactions.csv"
        )

        df = load_data(sample_path)
        st.sidebar.info("💡 Using sample transactions.csv")

    # -------------------------
    # Check whether data was loaded
    if df.empty:
        st.error("❌ No data loaded. Please check your CSV file.")
        st.stop()

    # -------------------------
    # Detect anomalies
    if 'is_anomaly' not in df.columns:
        df = detect_anomalies(df)

    # -------------------------
    # Sidebar Filters
    st.sidebar.subheader("🔍 Filter & Sort Transactions")

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

    if st.sidebar.button("Apply Filters"):
        st.session_state.filters_applied = True

    # -------------------------
    # Apply Filters
    if st.session_state.filters_applied:

        filtered_df = df[
            (df["Amount"] >= min_amt) &
            (df["Amount"] <= max_amt)
        ]

        if show_anomalies_only:
            filtered_df = filtered_df[
                filtered_df["is_anomaly"] == True
            ]

        if not filtered_df.empty:

            sort_column = st.sidebar.selectbox(
                "Sort By",
                options=filtered_df.columns,
                index=filtered_df.columns.get_loc("Amount")
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
        # Display Filtered Data
        st.subheader("📋 Filtered Transaction Data")

        st.dataframe(
            filtered_df,
            use_container_width=True
        )

        # -------------------------
        # Detailed Transaction View
        st.subheader("🔎 Detailed Transaction View")

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

            if "TransactionID" in filtered_df.columns:

                selected_row = filtered_df[
                    filtered_df["TransactionID"].astype(str)
                    == selected_id
                ]

            else:

                selected_row = filtered_df.loc[
                    [int(selected_id)]
                ]

            st.markdown("**Transaction Details:**")

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
            "Please adjust filters and click **Apply Filters** "
            "to update the results."
        )

else:

    st.info(
        "Please select a data source and click **Proceed** "
        "from the sidebar to begin processing."
    )