import glob
import json
import pandas as pd
import os

# Get a list of all JSON files in the specified directory
files = glob.glob('C:\\Users\\raju.kotyada\\Downloads\\FOSSE\\11\\*.json')

if not files:
    print("No JSON files found in the specified directory.")
else:
    # Loop through each file
    for file in files:
        print(f"Processing file: {file}")
        List_of_lines = []
        
        try:
            # Open and read the JSON file
            with open(file, 'r') as f:
                data = json.loads(f.read())
                
                # Check if 'Final_Response' exists in the data
                if 'Final_Response' in data:
                    # Loop through each item in 'Final_Response'
                    for d in data['Final_Response']:
                        # Check if 'dataframe' exists in the item
                        if d and 'dataframe' in d:
                            # Extract 'lineitem_desc', 'net_Amount', and 'submission_type' from each dataframe entry
                            for x in d['dataframe']:
                                lineitem_desc = str(x['lineitem_desc']).strip() if 'lineitem_desc' in x else 'lineitem_desc not available'
                                submission_type = d['submission_type'] if 'submission_type' in d else 'submission_type not available'
                                net_Amount = x['net_Amount'] if 'net_Amount' in x else 'net_Amount not available'
                                stat = x['stat'] if 'stat' in x else 'stat not available'
                                List_of_lines.append({'lineitem_desc': lineitem_desc, "net_Amount": net_Amount, "stat": stat, 'submission_type': submission_type})
                        else:
                            print(f"'dataframe' does not exist in {file}")
                else:
                    print(f"'Final_Response' does not exist in {file}")
        except Exception as e:
            print(f"Error processing file {file}: {e}")
        
        if List_of_lines:
            # Convert the list of dictionaries to a DataFrame
            df = pd.DataFrame(List_of_lines)

            # Get the base filename and replace .json with .xlsx
            base_filename = os.path.basename(file)
            excel_filename = os.path.splitext(base_filename)[0] + '.xlsx'
            excel_filepath = os.path.join('C:\\Users\\raju.kotyada\\Downloads\\FOSSE\\11\\', excel_filename)

            # Save the DataFrame to an Excel file
            df.to_excel(excel_filepath, index=False)

            print(f"Data successfully saved to {excel_filepath}")
        else:
            print(f"No data to save for {file}")


# # import glob
# # import json
# # import pandas as pd

# # List_of_lines = []
# # files = glob.glob('C:\\Users\\raju.kotyada\\Downloads\\FOSSE\\ALL\\*.json')
# # for file in files:
# #     print(file)

# #     with open(file, 'r') as f:
# #         data = json.loads(f.read())
# #         if 'Final_Response' in data:
# #             for d in data['Final_Response']:
# #                 if d and 'dataframe' in d:
# #                     List_of_lines += [
# #                         str(x['lineitem_desc']).strip() if 'lineitem_desc' in x else print('lineitem_desc not available ', x)
# #                         for x in d['dataframe']
# #                     ]
# #                 else:
# #                     print('dataframe not exists in', file)

# # List_of_lines = list(set(List_of_lines))  # Remove duplicates

# # # Convert List_of_lines to a DataFrame
# # df = pd.DataFrame(List_of_lines, columns=['lineitem_desc'])

# # # Save the DataFrame to an Excel file
# # excel_filename = 'C:\\Users\\raju.kotyada\\Downloads\\FOSSE\\ALL\\fosse.xlsx'
# # df.to_excel(excel_filename, index=False)
# # print(type(List_of_lines))

# import glob
# import json
# import pandas as pd

# # Initialize an empty list to store the extracted data
# List_of_lines = []

# # Get a list of all JSON files in the specified directory
# files = glob.glob('C:\\Users\\raju.kotyada\\Downloads\\FOSSE\\7\\*.json')

# # Loop through each file
# for file in files:
#     print(f"Processing file: {file}")

#     # Open and read the JSON file
#     with open(file, 'r') as f:
#         data = json.loads(f.read())
        
#         # Check if 'Final_Response' exists in the data
#         if 'Final_Response' in data:
#             # Loop through each item in 'Final_Response'
#             for d in data['Final_Response']:
#                 # Check if 'dataframe' exists in the item
#                 if d and 'dataframe' in d:
#                     # Extract 'lineitem_desc', 'net_Amount', and 'submission_type' from each dataframe entry
#                     for x in d['dataframe']:
#                         lineitem_desc = str(x['lineitem_desc']).strip() if 'lineitem_desc' in x else 'lineitem_desc not available'
#                         submission_type = d['submission_type'] if 'submission_type' in d else 'submission_type not available'
#                         net_Amount = x['net_Amount'] if 'net_Amount' in x else 'net_Amount not available'
#                         stat = x['stat'] if 'stat' in x else 'stat not available'
#                         List_of_lines.append({'lineitem_desc': lineitem_desc, "net_Amount": net_Amount, "stat" : stat, 'submission_type': submission_type})
#                         df = pd.DataFrame(List_of_lines)
#                 else:
#                     print(f"'dataframe' not exists in {file}")

# # Convert the list of dictionaries to a DataFrame
# df = pd.DataFrame(List_of_lines)

# # Save the DataFrame to an Excel file
# excel_filename = 'C:\\Users\\raju.kotyada\\Downloads\\FOSSE\\7\\fosse.xlsx'
# df.to_excel(excel_filename, index=False)

# print(f"Data successfully saved to {excel_filename}")
# print(type(List_of_lines))



# # import requests,json,glob
# # import pandas as pd

# # List_of_lines= []
# # files = glob.glob('C:\\Users\\raju.kotyada\\Downloads\\FOSSE\ALL\\*.json')
# # for file in files:
# #     print(file)

# #     with open(file,'r') as f:
# #         data = json.loads(f.read())
# #         if 'Final_Response' in data:
# #             for d in data['Final_Response']:
# #                 if d and  'dataframe' in d:
# #                     List_of_lines +=[str(x['lineitem_desc']).strip() if 'lineitem_desc' in x else print('lineitem_desc not available ',x)  for x in d['dataframe']]
# #                 else:
# #                     print('dataframe not exits in  ',file)


# # List_of_lines = list(set(List_of_lines))
# # res = json.loads(List_of_lines)
# # df = pd.json_normalize(res)
# # excel_filename = 'C:\\Users\\raju.kotyada\\Downloads\\FOSSE\ALL\\fosse.xlsx'
# # df.to_excel(excel_filename, index=False)
# # print(type(List_of_lines))