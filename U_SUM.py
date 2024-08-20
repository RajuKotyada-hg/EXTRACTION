import glob
import json
import pandas as pd
import os
import pdb

# Initialize an empty list to store the extracted data
List_of_lines = []

# Get a list of all JSON files in the specified directory
# files = glob.glob('D:\\OLD APPS\\Test\\pms\\HOTELKEY\\*.json')
files = glob.glob('C:\\Users\\raju.kotyada\\Downloads\\PMS_NEW_CHANGES\\choice advantage\\*.json')

# Loop through each file
for file in files:
    filename = os.path.basename(file)
    print(f"Processing file: {file}")

    # Open and read the JSON file
    with open(file, 'r') as f:
        data = json.loads(f.read())
        
        # Check if 'Final_Response' exists in the data
        if 'Final_Response' in data:
            # print("---------------------------------------------------------------")
            # print(data)
            # print("---------------------------------------------------------------")
            # Loop through each item in 'Final_Response'
            for d in data['Final_Response']:
                # Check if 'dataframe' exists in the item
                if d and 'dataframe' in d:
                    # Extract 'lineitem_desc', 'net_Amount', 'stat', and 'submission_type' from each dataframe entry
                    for x in d['dataframe']:
                        # print(x['lineitem_desc'])
                        # print(x['ps_curr_stat'])
                        # print(x)
                        head_matched = data['head_matched'][0] if 'head_matched' in data else ''
                        category = x['category'] if 'category' in x else ''
                        sub_category = x['sub_category'] if 'sub_category' in x else ''
                        if isinstance(x, dict):
                            ps_curr_stat = x.get('ps_curr_stat', '')
                        else:
                            ps_curr_stat = ''
                        # ps_curr_stat = x['ps_curr_stat'] if 'ps_curr_stat' in x else ''
                        # print(ps_curr_stat)
                        lineitem_desc = str(x['lineitem_desc']).strip() if 'lineitem_desc' in x else ''
                        actual_today_debits = x['actual_today_debits'] if 'actual_today_debits' in x else ''
                        adjusted_credits = x['adjusted_credits'] if 'adjusted_credits' in x else ''
                        net_amount = x['net_amount'] if 'net_amount' in x else ''
                        if isinstance(x, dict):
                            stat = x.get('stat', '')
                        else:
                            stat = ''
                        # stat = x['stat'] if 'stat' in x else ''
                        List_of_lines.append({'report_name': head_matched, 'category':category, 'sub_category':sub_category, 'ps_curr_stat':ps_curr_stat, 'lineitem_desc': lineitem_desc, "actual_today_debits": actual_today_debits, 'adjusted_credits' : adjusted_credits, 'net_amount':net_amount, 'stat': stat})
                else:
                    print(f"'dataframe' does not exist in {file}")

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(List_of_lines)

# Define the output directory
output_dir = 'C:\\Users\\raju.kotyada\\Downloads\\PMS_NEW_CHANGES\\choice advantage'

# Save the DataFrame to an Excel file
excel_filename = os.path.join(output_dir, 'output.xlsx')
df.to_excel(excel_filename, index=False)

# Save the List_of_lines to a JSON file
json_filename = os.path.join(output_dir, 'output.json')
with open(json_filename, 'w') as json_file:
    json.dump(List_of_lines, json_file, indent=4)

print(f"Data successfully saved to {excel_filename}")
print(f"JSON data successfully saved to {json_filename}")
print(type(List_of_lines))
