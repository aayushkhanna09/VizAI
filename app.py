import streamlit as st
import pandas as pd
import os

def load_data(uploaded_file):
    """Handles CSV and Excel file uploads."""
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            return pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
    return None

def main():
    st.set_page_config(page_title="Data Viz Lab Project", layout="wide")
    st.title("AI-Powered Business Data Analytics Tool")

    with st.sidebar:
        st.header("1. Upload Data")
        uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])
        st.markdown("---")
        
        if uploaded_file is not None:
            df = load_data(uploaded_file)
            if df is not None:
                st.sidebar.success("File uploaded successfully!")
                st.write("### Raw Data Preview")
                st.dataframe(df.head(10))
                st.markdown("---")
                
                # 1. Generate Summary Statistics
                st.subheader("Statistical Summary")
                st.write(df.describe())
                
                # 2. Identify Data Types and Missing Values
                st.subheader("Data Types & Missing Values")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Data Types**")
                    st.dataframe(df.dtypes.astype(str))
                    
                with col2:
                    st.write("**Missing Values**")
                    st.dataframe(df.isnull().sum())

if __name__ == "__main__":
    main()