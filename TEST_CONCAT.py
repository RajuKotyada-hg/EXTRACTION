import pandas as pd
import numpy as np
from re import sub
from decimal import Decimal
import camelot as cam
from tabulate import tabulate
import json,re,os

# Sample DataFrame (you would replace this with your actual data)


input_pdf = "D:\\OLD APPS\\Test\\Repository\\pms\\msi\\07\\Daily activity report 3-7-2024.pdf"

tables = cam.read_pdf(input_pdf, pages="all", flavor='stream', edge_tol=500)
# tables = cam.read_pdf(input_pdf, pages="all", flavor='stream')
for table in tables:
    df: pd.DataFrame = table.df
    print("-----------------------------------------rawdf-------------------------------------------------")
    print(df)
    print("-----------------------------------------rawdf-------------------------------------------------")

    # Step 1: Fill down the first column to propagate non-empty values
    df[0] = df[0].replace('', pd.NA).fillna(method='ffill')

    # Step 2: Group by the first column and concatenate strings for the second column and sum the numeric columns
    df_combined = df.groupby(0).agg({
        1: lambda x: ''.join(x),  # Concatenate descriptions without any separators
        2: 'sum',                 # Sum the numeric values in the third column
        3: 'sum'                  # Sum the numeric values in the fourth column
    }).reset_index()

    # Step 3: Clean up any extra spaces or special characters in the second column (index 1)
    df_combined[1] = df_combined[1].str.replace('[^a-zA-Z0-9 ]', '', regex=True).str.strip()

    # Display the result
    print(df_combined)
