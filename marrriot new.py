import re
import pandas as pd
from decimal import Decimal
from inspect import currentframe, getframeinfo
from tabulate import tabulate
import math
import json
# Extracting and cleaning the data from the loaded DataFrame


# Split the second column into Amount and the rest (Type and Description)

path = "D:\\OLD APPS\\Test\\Repository\\pms\\marriot fs\\CHINW.20240225.ij.txt"
df_file = pd.read_csv(path, header=None, names=["Data"])
print(df_file)

df_file[['Amount_Type', 'Description']] = df_file[1].str.extract(r'(\d+)([A-Z]+.*)')

# Further split the 'Amount_Type' into 'Amount' and 'Type'
df_file['Amount'] = df_file['Amount_Type'].str.extract(r'(\d+)')
df_file['Type'] = df_file['Amount_Type'].str.extract(r'([A-Z]+)')

# Drop the original columns we split
df_file_cleaned = df_file.drop(columns=[1, 'Amount_Type', 2, 3, 4])

# Rename columns for clarity
df_file_cleaned.columns = ['Identifier', 'Description', 'Currency', 'Amount', 'Type']

# Reorder columns for better readability
df_file_cleaned = df_file_cleaned[['Identifier', 'Amount', 'Type', 'Description', 'Currency']]

# Convert Amount to numeric
df_file_cleaned['Amount'] = pd.to_numeric(df_file_cleaned['Amount'], errors='coerce')

# Display the cleaned DataFrame
df_file_cleaned.head()
