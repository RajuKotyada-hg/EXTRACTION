import camelot
import pandas as pd

# Extract tables from the PDF using Camelot
tables = camelot.read_pdf('C://Users//raju.kotyada//Downloads//pms//pms//HOTELKEY//Final Audit (22).pdf', pages='all')

# Assuming the table of interest is the first one
df = tables[0].df

# The first row is assumed to be the header
df.columns = df.iloc[0]
df = df.drop(0).reset_index(drop=True)

# Convert the values to float and fill NaNs
for col in df.columns[1:-1]:
    df[col] = df[col].replace({'\$': '', ',': ''}, regex=True).astype(float)
df = df.fillna(0)

# Format the output
output = df.drop(columns=['Category']).applymap(lambda x: f"${x:.2f}" if isinstance(x, (int, float)) else x)

# Add extra space to 'Description' column to match output format
output['Description'] = output['Description'].str.pad(width=30)

# Print output
print(output.to_string(index=False))
