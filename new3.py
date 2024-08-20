import pandas as pd
import re

# Step 1: Read the text file
with open('D:\\FOSSE\\7\\D A I L Y   C L O S I N G   R E P O R T   S U M M A R Y-7thjuly.txt', 'r') as file:
    lines = file.readlines()

# Step 2: Preprocess the Data
def preprocess_line(line):
    # Remove extra spaces and normalize delimiters
    line = re.sub(r'\s*\|\s*', ' | ', line.strip())  # Normalize pipe delimiters
    return line

# Clean lines
lines = [preprocess_line(line) for line in lines]

# Step 3: Identify and Extract Table Data
def extract_table(lines):
    tables = []
    table_data = []
    current_table_name = None

    for line in lines:
        if line.startswith('Table'):
            if table_data:
                tables.append((current_table_name, table_data))
                table_data = []
            current_table_name = line.split(':')[1].strip()
        elif line.strip() == "":
            if table_data:
                tables.append((current_table_name, table_data))
                table_data = []
            current_table_name = None
        else:
            table_data.append(line)

    if table_data:
        tables.append((current_table_name, table_data))

    return tables

tables = extract_table(lines)

# Step 4: Convert to DataFrame
def convert_to_dataframe(table_data):
    header = table_data[0].split(' | ')
    rows = [line.split(' | ') for line in table_data[1:]]
    return pd.DataFrame(rows, columns=header)

# Save tables to CSV
for table_name, data in tables:
    if data:
        df = convert_to_dataframe(data)
        df.to_csv(f'{table_name.replace(" ", "_")}.csv', index=False)
        print(f"Table: {table_name}")
        print(df)
        print()

