import streamlit as st
import pandas as pd

st.title("📂 Upload Dataset")

uploaded_file = st.file_uploader(
    "Choose an Excel file",
    type=["xlsx"]
)

if uploaded_file is not None:

    df = pd.read_excel(uploaded_file)

    st.session_state["df"] = df

    st.success("Dataset Loaded Successfully!")

    st.subheader("Dataset Preview")
    st.dataframe(df)

    st.subheader("Shape")
    st.write(df.shape)

    st.subheader("Columns")
    st.write(df.columns.tolist())

    st.subheader("Data Types")
    st.dataframe(
        df.dtypes.astype(str)
        .reset_index()
        .rename(columns={"index": "Column", 0: "Data Type"})
    )

    st.subheader("Missing Values")
    st.dataframe(
        df.isnull()
        .sum()
        .reset_index()
        .rename(columns={"index": "Column", 0: "Missing Values"})
    )

    st.subheader("Duplicate Rows")
    st.write(df.duplicated().sum())

    st.subheader("Summary Statistics")
    st.dataframe(df.describe())