import streamlit as st
import pandas as pd
import os
import plotly.express as px
from dotenv import load_dotenv
from pandasai_litellm.litellm import LiteLLM
import pandasai as pai

# Load environment variables immediately
load_dotenv()

def load_data(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            return pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error loading file: {e}")
    return None

def main():
    st.set_page_config(page_title="LLM+DV project", layout="wide")
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
                
                st.subheader("Statistical Summary")
                st.write(df.describe())
                
                st.subheader("Data Types & Missing Values")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Data Types**")
                    st.dataframe(df.dtypes.astype(str))
                    
                with col2:
                    st.write("**Missing Values**")
                    st.dataframe(df.isnull().sum())
                    
                st.markdown("---")
                
                st.subheader("Create Custom Charts")
                columns = df.columns.tolist()
                
                col_x, col_y, col_type = st.columns(3)
                
                with col_x:
                    x_axis = st.selectbox("Select X-axis", options=["Select..."] + columns)
                with col_y:
                    y_axis = st.selectbox("Select Y-axis", options=["Select..."] + columns)
                with col_type:
                    chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot"])
                
                if x_axis != "Select..." and y_axis != "Select...":
                    try:
                        if chart_type == "Bar Chart":
                            fig = px.bar(df, x=x_axis, y=y_axis)
                        elif chart_type == "Line Chart":
                            fig = px.line(df, x=x_axis, y=y_axis)
                        elif chart_type == "Scatter Plot":
                            fig = px.scatter(df, x=x_axis, y=y_axis)
                            
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Could not generate chart: {e}")
                        st.markdown("---")
                
                
                st.subheader("Test AI Connection")
                
                api_key = os.getenv("GEMINI_API_KEY")
                
                if not api_key:
                    st.warning("⚠️ GEMINI_API_KEY is missing. Please add it to your .env file.")
                else:
                    try:
                        # 1. Initialize the LLM
                        llm = LiteLLM(model="gemini/gemini-2.5-flash", api_key=api_key)
                        pai.config.set({"llm": llm})
                        
                        # 2. Create the SmartDataframe
                        sdf = pai.SmartDataframe(df)
                        
                        # 3. Hardcoded Test
                        if st.button("Test AI: Count Rows"):
                            with st.spinner("Asking Gemini..."):
                                response = sdf.chat("How many rows are in this dataset?")
                                st.success("AI Response:")
                                st.write(response)
                                
                    except Exception as e:
                        st.error(f"Failed to initialize AI: {e}")

if __name__ == "__main__":
    main()