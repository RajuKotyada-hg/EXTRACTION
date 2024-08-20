import json
import pandas as pd

# Read sheet1.json file
with open('C:\\Users\\raju.kotyada\\Downloads\\Fosse 1 (1)\\fosse\\fosse.json', 'r') as f:
    sheet1_data = json.load(f)

# Read snippet2.json file
with open('D:\\FOSSE\\daily_sales.properties_northwest.json', 'r') as f:
    snippet2_data = json.load(f)

# Create a dictionary to map line_item to label
line_item_to_label = {item['line_item']: item['label'] for item in snippet2_data['labels']}

# Process sheet1_data and add category based on line_item match
processed_data = []
for item in sheet1_data:
    lineitem_desc = item['lineitem_desc']
    if lineitem_desc in line_item_to_label:
        item['category'] = line_item_to_label[lineitem_desc]
    else:
        item['category'] = 'Unknown'
    processed_data.append(item)

# Convert the processed data to a DataFrame
df = pd.DataFrame(processed_data)

# Save the DataFrame to a CSV file
csv_filename = 'D:\\FOSSE\\processed_data.csv'
df.to_csv(csv_filename, index=False)

print(f"Data successfully saved to {csv_filename}")
print(type(processed_data))
