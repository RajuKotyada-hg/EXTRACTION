import re
import pandas as pd
from decimal import Decimal
from inspect import currentframe, getframeinfo
from tabulate import tabulate
import math
import numpy as np
import json


class MarriotDFPreparationTool:
    def __init__(self, cfg, filename) -> None:
        self.data = {}
        self.pattern = cfg['patternmfs']
        self.head = cfg['head']
        self.exception_words = cfg['patternmfs'][0]['ExceptionWords']
        self.column_headers = cfg['patternmfs'][0]['column_headers']
        self.columns = cfg['patternmfs'][0]['columns']
        self.ignore_contains = cfg['patternmfs'][0]['IgnoreContains']
        self.columnHeaders = cfg['patternmfs'][0]['columnHeaders']
        self.signChange = cfg['patternmfs'][0]['signChange']
        self.lineitem_desc = cfg['patternmfs'][0]['lineitem_desc']
        self.today_actual_debits = cfg['patternmfs'][0]['today_actual_debits']
        self.stat = cfg['patternmfs'][0]['stat']
        self.submission_type = cfg['patternmfs'][0]['submission_type']
        self.filename = filename

    def read_data(self, path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(path, header=None, names=["Data"])
        except FileNotFoundError:
            print(f"File '{path}' not found.")
            exit(1)  # Exit the program if the file is not found
        return df

    def extract_data(self, df: pd.DataFrame, columnHeaders: list) -> pd.DataFrame:
        try:
            pattern = r'(\d+)\s*(CR|DR)(.*)\s+([A-Z]+)'
            df[columnHeaders] = df["Data"].str.extract(pattern)
            df = df.drop(columns=["Data"])
        except Exception as e:
            print(f"🐞🐞 Error in extract_data: {e}")
        return df

    def process_stats_column(self, df: pd.DataFrame, ignore_contains: list) -> pd.DataFrame:
        try:
            df['Stats'] = None
            df['ps_curr_stat'] = 'USD'  # Default currency
            df['Description'] = df['Description'].astype(str).str.strip()

            # Filter out rows based on ignore_contains keywords
            for keyword in ignore_contains:
                df = df[~df['Description'].str.contains(keyword, case=False)]

            # Create mask for rows with 'STAT' or 'STATS'
            stat_mask = df['Description'].str.contains(r'\bSTAT\b|\bSTATS\b', case=False, regex=True)
            
            # Set 'Stats' and 'Amount' for 'STAT' or 'STATS' rows
            df.loc[stat_mask, 'Stats'] = df.loc[stat_mask, 'Amount'].astype(str)
            df.loc[stat_mask, 'Amount'] = None
            df.loc[stat_mask, 'ps_curr_stat'] = 'RM'  # Set currency to RM
            
            # For rows without 'STAT' or 'STATS', ensure 'ps_curr_stat' is 'USD'
            df.loc[~stat_mask, 'ps_curr_stat'] = 'USD'

            # Clean up 'Stats' values
            # df['Stats'] = df['Stats'].str.replace(r'00$', '', regex=True)
            # df['Stats'] = pd.to_numeric(df['Stats'], errors='coerce')
            # # df = df[np.isfinite(df['Stats'])]
            df['Stats'] = df['Stats'].astype(int)
            # df['Stats'] = df['Stats'].fillna(0).astype(int)
                        
            df['Stats'] = df['Stats'].str.replace(r'00$', '', regex=True)

            # Convert the 'Stats' column to numeric, turning non-numeric values into NaN
            df['Stats'] = pd.to_numeric(df['Stats'], errors='coerce')

            # Replace NaN values with an empty string
            df['Stats'] = df['Stats'].fillna('')
            df['Stats'] = df['Stats'].astype(int)
            
        except Exception as e:
            print(f"🐞🐞 Error in process_stats_column: {e}")
            
        return df


    # def process_stats_column(self, df: pd.DataFrame, ignore_contains: list) -> pd.DataFrame:
    #     try:
    #         df['Stats'] = None
    #         df['Description'] = df['Description'].astype(str).str.strip()  # Ensure the column is treated as strings

    #         for keyword in ignore_contains:
    #             df = df[~df['Description'].str.contains(keyword)]

    #         df.loc[df['Description'].str.contains(r'\bSTAT\b|\bSTATS\b'), 'Stats'] = df['Amount'].astype(str)
    #         df.loc[df['Description'].str.contains(r'\bSTAT\b|\bSTATS\b'), 'Amount'] = None
    #         df['Stats'] = df['Stats'].str.replace(r'00$', '', regex=True)
    #         df['Stats'] = pd.to_numeric(df['Stats'], errors='coerce')
    #         df['Stats'] = df['Stats'].fillna(0).astype(int)
    #     except Exception as e:
    #         print(f"🐞🐞 Error in process_stats_column: {e}")
    #     return df

    def make_amount_decimal(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df["Amount"] = df["Amount"].str[:-2] + "." + df["Amount"].str[-2:]
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        except Exception as e:
            print(f"🐞🐞 Error in make_amount_decimal: {e}")
        return df

    def custom_amount(self, row: pd.Series, exception_words: list, signChange: bool) -> float:
        try:
            if any(word in row['Description'] for word in exception_words):
                if signChange:
                    return -row['Amount'] if row['Transaction_type'] == 'CR' else row['Amount']
                else:
                    return row['Amount'] if row['Transaction_type'] == 'CR' else row['Amount']
            if signChange:
                return -row['Amount'] if row['Transaction_type'] == 'DR' else row['Amount']
            else:
                return row['Amount'] if row['Transaction_type'] == 'DR' else row['Amount']
        except Exception as e:
            print(f"🐞🐞 Error in custom_amount: {e}")
        return row['Amount']

    def add_lineitem_col(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df['lineitem_desc'] = df[self.lineitem_desc]
        except Exception as e:
            print(f"🐞🐞 Error in add_lineitem_col: {e}")
        return df

    def add_netAmount_col(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df['today_actual_debits'] = df[self.today_actual_debits]
        except Exception as e:
            print(f"🐞🐞 Error in add_netAmount_col: {e}")
        return df

    def add_stat_col(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df['stat'] = df[self.stat]
        except Exception as e:
            print(f"🐞🐞 Error in add_stat_col: {e}")
        return df
    
    def add_desc_col(self,  df : pd.DataFrame):
        try:
            df[self.column_headers] = df[self.columns]
        except Exception as e:
            print('🐞🐞 Error while add_lineitem_col: ', e)
        return df

    def apply_PMS_rules(self, df: pd.DataFrame) -> dict:
        output = {'dataframe': df}
        try:
            if self.lineitem_desc or self.lineitem_desc == 0:
                df = self.add_lineitem_col(df)
            
            if self.column_headers or self.columns == 0:
                df = self.add_desc_col(df)

            if self.today_actual_debits != False:
                df = self.add_netAmount_col(df)

            if self.stat != False:
                df['stat'] = df[self.stat]

            if self.submission_type != False:
                output['submission_type'] = self.submission_type

            output = {'dataframe': df.to_dict(orient='records')}
        except Exception as e:
            print(f"🐞🐞 Error in apply_PMS_rules: {e}")
        return output

    def ignore_contains(self, df: pd.DataFrame, config: list | None = None) -> pd.DataFrame:
        if not isinstance(config, list):
            print("🐞🐞 ValueError: ignore_contains failed.")
            return df
        try:
            mask = ~df.apply(lambda row: any(word in str(row) for word in config), axis=1)
            df = df[mask]
        except Exception as e:
            print(f"🐞🐞 Error in ignore_contains: {e}")
        return df

    def startPreparation(self) -> list:
        match_heads = []
        try:
            with open(self.filename, 'r') as F:
                if re.search(pattern=self.head, string=F.read(), flags=re.DOTALL) is not None:
                    match_heads.append(self.head)
                else:
                    print('header not found', self.head)

            df = self.read_data(self.filename)
            print(df.to_string())
            df = self.extract_data(df, self.columnHeaders)
            df = self.process_stats_column(df, self.ignore_contains)
            df = self.make_amount_decimal(df)
            df['Amount'] = df.apply(self.custom_amount, axis=1, args=(self.exception_words, self.signChange))
            res = self.apply_PMS_rules(df)
            print(df)
            if self.submission_type != False:
                res['submission_type'] = self.submission_type

            keys_to_keep = ['lineitem_desc', 'today_actual_debits', 'stat', 'category', 'ps_curr_stat']
            for row in res['dataframe']:
                for key in list(row.keys()):
                    if key not in keys_to_keep:
                        row.pop(key)
                for key in list(row.keys()):
                    if pd.isna(row[key]):
                        del row[key]
            print("----------------------------------final----------------------------------------")
            print(res)
            return [[res], match_heads]
        except Exception as e:
            print(f"🐞🐞 Error in startPreparation: {e}")
            return []

    @staticmethod
    def preInitiate(cfg, filename):
        initiate = MarriotDFPreparationTool(cfg, filename)
        return initiate.startPreparation()
    
with open('temp.json', 'r') as data_file:
    cfg: dict = json.load(data_file)
filename = "D:\\OLD APPS\\Test\\Repository\\Done\\marriot fs\\feb\\CHINW.20240223.ij.txt"
tool = MarriotDFPreparationTool(cfg[0], filename)
results, match_heads = tool.startPreparation()
    
    

