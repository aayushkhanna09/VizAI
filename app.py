import streamlit as st
import pandas as pd
import os
import plotly.express as px
from dotenv import load_dotenv
from pandasai_litellm.litellm import LiteLLM
import pandasai as pai

load_dotenv()

def load_data(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            return pd.read_excel(uploaded_file)
    except pd.errors.EmptyDataError:
        st.error("The uploaded file is empty. Please upload a valid dataset.")
    except ValueError:
        st.error("Invalid file format or corrupted data.")
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
                if df.empty or len(df.columns) == 0:
                    st.error("The uploaded file is empty. Please add data before uploading.")
                else:
                    df = df.dropna(how='all')
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
                
                
                    st.subheader("💬 Ask your Data")
                
                
                    os.makedirs("exports/charts", exist_ok=True)
                
                
                    api_key = os.getenv("GEMINI_API_KEY")
                    if not api_key:
                        st.warning("⚠️ GEMINI_API_KEY is missing. Please add it to your .env file.")
                    else:
                    
                        llm = LiteLLM(model="gemini/gemini-2.5-flash", api_key=api_key)
                    
                        pai.config.set({"llm": llm, "save_charts": True, "save_charts_path": "exports/charts"})
                        sdf = pai.SmartDataframe(df)

                        if "messages" not in st.session_state:
                            st.session_state.messages = []

                   
                        for message in st.session_state.messages:
                            with st.chat_message(message["role"]):
                                if message.get("is_image"):
                                    st.image(message["content"])
                                else:
                                    st.markdown(message["content"])

                   
                        if prompt := st.chat_input("E.g., What is the total revenue? Show me a bar chart of sales by region."):
                        
                        
                            st.session_state.messages.append({"role": "user", "content": prompt, "is_image": False})
                            with st.chat_message("user"):
                                st.markdown(prompt)

                        
                            with st.chat_message("assistant"):
                                with st.spinner("Analyzing data..."):
                                    try:
                                        response = sdf.chat(prompt)
                                    
                                    
                                        if isinstance(response, str) and response.endswith('.png'):
                                            st.image(response)
                                            st.session_state.messages.append({"role": "assistant", "content": response, "is_image": True})
                                        else:
                                            st.write(response)
                                            st.session_state.messages.append({"role": "assistant", "content": str(response), "is_image": False})
                                        
                                    except Exception as e:
                                        st.error("The AI couldn't process that request. Try rephrasing.")
                                        st.error(str(e))

if __name__ == "__main__":
    main()