import pandas as pd
import re

# # Replace 'file_path.csv' with the path to your CSV file
# path = "D:\\OLD APPS\\Test\\Repository\\pms\\marriot fs\\CHINW.20240225.ij.txt"
# df = pd.read_csv(path, header=None, names=["Data"])

# columnHeaders= ["Amount" , "Transaction_type" , "Description" , "Currency"]
# pattern = r'(\d+)\s*(CR|DR)(.*)\s+([A-Z]+)'
# df[columnHeaders] = df["Data"].str.extract(pattern)
# df["Amount"] = df["Amount"].str[:-2] + "." + df["Amount"].str[-2:]
# df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
# df = df.drop(columns=["Data"])
# # Display the first few rows of the DataFrame
# print(df.to_string())

# filename = "D:\\FOSSE\\7\\D A I L Y   C L O S I N G   R E P O R T   S U M M A R Y-7thjuly.txt"
filename = "D:\\FOSSE\\7\\D A I L Y   C L O S I N G   R E P O R T   S U M M A R Y-7thjuly.txt"
with open(filename,'r') as F:
    df = pd.DataFrame(F) 
    df = df.apply(lambda x: x.str.replace('-', ''))
    df = df.apply(lambda x: x.str.replace('\n', ''))
    # df_split = df[0].str.split(r'\s{2,}', expand=True)
    # df_split = df.fillna('')
    # df_split =df_split.reindex()
    # df = df.apply(lambda x: x.str.replace('None', ''))
    # print(df.to_string())
    # print(df_split.to_string())
    # for line in F:
    #     # print(type(F))
    df = df[0].str.split(r'\s{2,}', expand=True)
    df = df.fillna('')
    # print(df)
    print(df.to_string())

    # Step 2: Rename the columns according to their index numbers (if needed)
    # df = [str(i) for i in range(df.shape[1])]

    # Step 3: Replace the original DataFrame with the split columns
    # df = pd.concat([df], axis=1)

    # Optional: Replace None with empty strings if necessary
    # df = df.fillna('')

        # df_split = df['text_column'].str.split(r'\s{2,}', expand=True)
        # df['column1'] = df['column1'].str.replace('-', '', regex=False)
    # if(re.search(string=F.read(),flags=re.DOTALL) is not None) :
    
