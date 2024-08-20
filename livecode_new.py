import pandas as pd
import numpy as np
from re import sub
from decimal import Decimal
import camelot as cam
from tabulate import tabulate
import json,re,os

# pd.options.mode.copy_on_write = True # For eliminate pandas warning

class DataFramePreparation:
    def __init__(self, config: dict):
        self.actual_today_debits = config.get('actual_today_debits', False)
        self.adjusted_credits = config.get('adjusted_credits', False)
        self.net_amount = config.get('net_amount', False)
        self.stat = config.get('stat', False)
        self.ref_col = config.get('ref_col', False)
        self.submission_type = config.get('submission_type', False)
        self.lineitem_desc_label = config.get('lineitem_desc_label', False)
        self.cn1 = config.get('cn1', False)
        self.cn2 = config.get('cn2', False)
        self.cn3 = config.get('cn3', False)
        self.column_headers = config.get('column_headers', False)
        self.columns = config.get('columns', False)
        
        
    #methods
    def check_newlines_and_currencies(self, x):
        # print("🌸", x, "🌸")
        sx = str(x).strip()
        
        if sx.find("\n|\t") >= 0:
            # print("new line 🔗")
            return [y for y in sx.split("\n|\t") if y]

        if sx.find("/") >=0: # skip dates
            # print("date 📅")
            return x
        
        if sx.find("%") >= 0: # skip percentages
            # print("percentage 🧮")
            return x
        
        if sx.count("$") > 1:
            tx = [y for y in sx.split("$") if y]
            res = []
            for t in tx:
                try:
                    d = Decimal(sub(r'[^\d.]','',t))
                    if t.find("(") >= 0 or t.find(")") >= 0:
                        d = -d
                    res.append(float(d))
                except:
                    pass
            # print("currencies 💰💰", res)
            return res
        
        
        if sx.count("$") > 0:
            try:
                dd = Decimal(sub(r'[^\d.]','',x))
                if x.find("(") >= 0 or x.find(")") >= 0:
                    dd = -dd
                # print("currency 💰", dd)
                return float(dd)
            except:
                # print("nothing $🎈")
                return x
        # print("nothing e🎈")

        if isinstance(x, str):
            return x.strip()
        else:
            return x
        
        return str(x).strip()

    def maxlen(self, x):
        return max([len(item) for item in x if type(item)==list], default=0)

    def normalizelists(self, x):
        maxlen = x['len'] 
        if maxlen == 0: return x
        row = []
        for item in x:
            if type(item) == list: 
                item.extend([np.NaN] * (maxlen - len(item)))
                row.append(item)
            else:
                y= [item]
                y.extend([np.NaN] * (maxlen - 1))
                row.append(y)
        return row

    def check_newlines_spilt_cols(self, r,pref,rc):
        if rc==2:
            result = ['','']
            R =str(r).split('\n|\t')
            if len(R)>1:return [R[0].strip(),R[1].strip()]
            else:
                result[pref]=r
                return result
    
    def format_desc(self,row,extention):
        return str(extention)+' '+str(row)
    
    def is_number(self,string):
        pattern = r'^[+-]?\d{1,3}(,\d{3})*(\.\d+)?$'
        match = re.match(pattern, string)
        return bool(match)
    
    def contains_alpha_or_special(self,string):
        pattern = r'[a-zA-Z!@#$%^&*()]'
        match = re.search(pattern, string)
        return match is not None
    
    def format_amount(self,t):
        try:
            if isinstance(t,float) or  isinstance(t,int):return t
            if t == '':return 0
            # d = Decimal(sub(r'[^\d.]','',t))
            d = Decimal(sub(r'[^\d.-]', '', t))
            if t.find("(") >= 0 or t.find(")") >= 0: d = -d
            return float(d)
        except Exception as x: 
            if(self.is_number(str(t).strip()) or str(t).strip() =='.00' or self.contains_alpha_or_special(str(t).strip())=='-'):
                
            # if(self.is_number(str(t).strip()) or str(t).strip() =='.00' or self.contains_alpha_or_special(str(t).strip())==False):
                return t
            else:return 0    

    def clean_dataFrame(self, df:pd.DataFrame):
        try:
            df.dropna(how="all", axis=1, inplace=True ) # Drop column if entire column is Nan 
            df.dropna(how="all", axis=0, inplace=True )# Drop row if entire column is Nan 
            df.set_index( np.arange(0, len(df)), inplace=True)
            df.reindex()
        except Exception as e:
            print('🐞🐞 Error while cleaning df : ', e)
        return df

    #functions
    def process_dataframe(self, df:pd.DataFrame, config : dict):
        function_mapping = {
            'replace_na':self.replace_na,
            
            'split_cols':self.split_cols,
            'drop_empty_and_shift_left':self.drop_empty_and_shift_left,
            'ignore_contains':self.ignore_contains,
            'remove_head': self.remove_head,
            'remove_tail': self.remove_tail,
            
            'merge_cols': self.merge_cols,
            'merge_rows': self.merge_rows,

            'swap_cols': self.swap_cols,
            'swap_rows': self.swap_rows,
            
            'drop_row_with_empty_cols': self.drop_row_with_empty_cols,
            'drop_col_with_empty_row': self.drop_col_with_empty_row,

            'remove_repeating_headers':self.remove_repeating_headers,
        
            'split_rows':self.split_rows, 
            'shift_rows': self.shift_rows,

            "remove_rows_with":self.remove_rows_with, 
            'add_only_rows_with':self.add_only_rows_with,

            'split_stat_amount':self.split_stat_amount,
            "drop_empty_cols": self.drop_empty_cols,
            'combine_rows': self.combine_rows
        }

        df = self.clean_dataFrame(df)

        for key, function in function_mapping.items():
            if key in config.keys():
                df = self.clean_dataFrame(function(df, config[key]))

        # if 'triggers' in config:
        #     final_data = self.triggers(df, config['triggers'])
        # else:
        #     final_data = [self.Apply_PMS_Rules(df, [])]
        # return final_data

        if 'triggers' in config:
            print("-------------------------------triggers------------------------------------------")
            filtered_data = self.triggers(df, config['triggers'])
            final_data = []

            for item in filtered_data:
                # dataframe = item['dataframe']
                # filtered_dataframe = [row for row in dataframe if row.get('lineitem_desc', '') != '' or row.get('actual_today_debits', '') != '']
                # filtered_dataframe = [row for row in dataframe if row['lineitem_desc'] != '']
                # filtered_dataframe = [row for row in dataframe if row['actual_today_debits'] != ' ' or row['stat'] != ' '] 
                # filtered_dataframe = [row for row in dataframe if row['lineitem_desc'] != '']
                # for row in filtered_dataframe['dataframe']:
                #     for key in list(row.keys()):
                #         if pd.isna(row[key]):
                #             del row[key]
                # filtered_dataframe = [row for row in dataframe if row['lineitem_desc'] != '' or row['actual_today_debits']>0]
                # filtered_dataframe = [row for row in dataframe if row['lineitem_desc'] != '']
                # filtered_dataframe = [row for row in dataframe if row['actual_today_debits'] != '']
                # filtered_dataframe = dataframe[(dataframe['lineitem_desc'] != '') | (dataframe['actual_today_debits'] != '')]
                # filtered_dataframe = [row for row in dataframe if row['lineitem_desc'] != ' ']
                # filtered_dataframe = [row for row in dataframe if row['lineitem_desc'] != ' ' or row['lineitem_desc'] != 'nan' or 'actual_today_debits' in row]
                # filtered_dataframe = [row for row in dataframe if (row.get('lineitem_desc', '').strip() not in ['', 'nan']) or ('actual_today_debits' in row)]
                # item['dataframe'] = filtered_dataframe
                final_data.append(item)
            # print(final_data)
            print("---------------------------------triggers----------------------------------------")
        else:
            print("-----------------------------Nontriggers--------------------------------------------")
            # print(config)
            if 'extension' in config:  
                self.extention = config['extension']
            if 'category' in config:
                if 'cn1' in config:
                    df[self.cn1] = config['category']
                else:
                    df['category'] = config['category']
            if 'sub_category' in config:
                if 'cn2' in config:
                    df[self.cn2] = config['sub_category']
                else:
                    df['sub_category'] = config['sub_category']
            if 'ps_curr_stat' in config:
                if 'cn3' in config:
                    df[self.cn3] = config['ps_curr_stat']
                else:
                    df['ps_curr_stat'] = config['ps_curr_stat']

            
            
            # if "category" in config:
            #     df[self.cn1] = config["category"]
            # if "sub_category" in config:
            #     df[self.cn2] = config["sub_category"]
            # if "ps_curr_stat" in config:
            #     df[self.cn3] = config["ps_curr_stat"]
            x = [self.Apply_PMS_Rules(df, [],[],[],[],[])]
            filtered_data = list(filter(lambda item: item is not None, x))
            # x = [self.Apply_PMS_Rules(df, [],[])]
            # filtered_data = list(filter(lambda item: item is not None, x))
            final_data = []

            for item in filtered_data:
                dataframe = item['dataframe']  
                # filtered_dataframe = [row for row in dataframe if row['lineitem_desc'] != '']
                # filtered_dataframe = [row for row in dataframe if row['lineitem_desc'] != '  ']
                # for row in filtered_dataframe['dataframe']:
                #     for key in list(row.keys()):
                #         if pd.isna(row[key]):
                #             del row[key]
                # filtered_dataframe = [row for row in dataframe if row.get('lineitem_desc', '') != '' or row.get('actual_today_debits', '') != '']
                # filtered_dataframe = [row for row in dataframe if row['lineitem_desc'] != '' or row['actual_today_debits'] != '' or row['lineitem_desc'].notna()]
                # filtered_dataframe = [row for row in dataframe if row['lineitem_desc'] != '']
                # filtered_dataframe = [row for row in dataframe if row['actual_today_debits'] != '']
                # filtered_dataframe = dataframe[(dataframe['lineitem_desc'] != '') | (dataframe['actual_today_debits'] != '')]
                # filtered_dataframe = [row for row in dataframe if row['lineitem_desc'] != '' or {'actual_today_debits' in row}]
                # filtered_dataframe = [row for row in dataframe if (row.get('lineitem_desc', '').strip() not in ['', 'nan']) or ('actual_today_debits' in row)]
                # item['dataframe'] = filtered_dataframe
                final_data.append(item)
            # print(final_data)
            print("-------------------------------Nontriggers------------------------------------------")

        return final_data

    def replace_na(self, df: pd.DataFrame, config: bool | None = None):
        if not isinstance(config, bool) or config  == False:
            print("🐞🐞 ValueError: replace_na failed due to a data type mismatch.")
            return df  

        try:
            df.replace(np.nan, '', axis=1, inplace=True)
            df.replace(np.nan, '', axis=0, inplace=True)

        except Exception as e:
            print('🐞🐞Error while replace_na: ', e)

        return df

    def drop_empty_and_shift_left(self, df: pd.DataFrame, config: bool | None = None):
        if not isinstance(config, bool):
            print("🐞🐞 ValueError: shift_rows failed due to a data type mismatch.")
            return df
        try:
            print("-------------------------------drop_empty_and_shift_left------------------------------------------")
            rows = []
            df.replace("", np.nan, inplace=True)
            for idx, row in df.iterrows():
                # Drop NaN values
                row_dropped = row.dropna()
                # Shift values to the left
                row_shifted = row_dropped.tolist() + [np.nan] * (len(row) - len(row_dropped))
                rows.append(row_shifted)
            df = pd.DataFrame(rows, columns=df.columns).reset_index(drop=True)
            df.dropna(how="all", axis=1, inplace=True)
            print("-------------------------------drop_empty_and_shift_left------------------------------------------")
        except Exception as e:
            print('🐞🐞Error occurred while shifting rows:', e)

        return df

    def ignore_contains(self,  df : pd.DataFrame, config:list | None = None):
        if not isinstance(config, list):
            print("🐞🐞 ValueError: ignore_contains failed.")
            return df
        try:
            # Use .applymap to check element-wise, then use .any(axis=1) to check row-wise
            mask = ~df.apply(lambda row: any(word in str(row) for word in config), axis=1)
            df = df[mask]
          
        except Exception as e:
            print('🐞🐞 Error while remove rows with: ', e)

        return df

    def remove_head(self, df:pd.DataFrame, config:int | None = None):
        if not isinstance(config, int):
            print("🐞🐞 ValueError: remove_head failed due to a data type mismatch.")
            return df
        try:
            df.drop(df.head(config).index, inplace=True)
        except Exception as e:
            print('🐞🐞 Error while removing head : ', e)
        return df
        
    def remove_tail(self, df:pd.DataFrame, config:int | None = None):

        if not isinstance(config, int):
            print("🐞🐞 ValueError: remove_tail failed due to a data type mismatch.")
            return df
        
        try:
            df.drop(df.tail(config).index, inplace=True )
        except Exception as e:
            print('🐞🐞 Error while removing tail : ', e)
        return df
    
    def swap_rows(self, df:pd.DataFrame, config:list | None = None):
        if not isinstance(config, list):
            print("🐞🐞 ValueError: swap_rows failed due to a data type mismatch.")
            return df       
        try:
            for sr in config:
                df.iloc[sr+1] = df.iloc[sr+1].combine_first(df.iloc[sr])
            df.drop(index=df.index[config], inplace=True)

        except Exception as e:
            print('🐞🐞 Error while swap rows: ', e)

        return df

    def swap_cols(self, df:pd.DataFrame, config:list | None = None):
        if not isinstance(config, list):
            print("🐞🐞 ValueError: swap_cols failed due to a data type mismatch.")
            return df     
        try:
            for sr in config:
                df.iloc[:,sr+1] = df.iloc[:,sr+1].combine_first(df.iloc[:,sr])
            df.drop(columns=df.columns[config], inplace=True)

        except Exception as e:
            print('🐞🐞Error while swap columns: ', e )
        return df  

    def drop_row_with_empty_cols(self, df:pd.DataFrame, config:list | None = None):
        if not isinstance(config, list):
            print("🐞🐞 ValueError: drop_row_with_empty_cols failed due to a data type mismatch.")
            return df     
        try:
            for eci in config:
                col_index = df.columns[eci]
                df.dropna(subset=[col_index], inplace=True)
        except Exception as e:
            print('🐞🐞Error occur while drop row with empty columns: ', e)
        return df

    def drop_col_with_empty_row(self, df:pd.DataFrame, config:int | None = None):
        if not isinstance(config, int):
            print("🐞🐞 ValueError: drop_col_with_empty_row failed due to a data type mismatch.")
            return df  
        try:
            df.dropna(axis=1,thresh=config, inplace=True)
        except Exception as e:
            print('🐞🐞Error while drop column with empty rows: ', e)
        return df

    def split_rows(self, df:pd.DataFrame, config:bool | None = None):
        if not isinstance(config, bool) or config  == False:
            print("🐞🐞 ValueError: split_rows failed due to a data type mismatch.")
            return df  
        try:
            for col in df.columns:
                df[col].replace(np.nan, "", inplace=True)
                df[col] = df[col].apply(self.check_newlines_and_currencies)    
            
            df["len"] = df.apply(lambda row: self.maxlen(row), axis=1)
            df = df.apply(lambda row: self.normalizelists(row), axis=1)
            df.drop(columns=['len'], inplace=True)
            df = df.explode(df.columns.tolist()).reset_index(drop=True)
        except Exception as e:
            print('🐞🐞 Error occur at split rows function', e)
        return df

    def split_cols(self,  df : pd.DataFrame, config:list | None = None):
        if not isinstance(config, list):
            print("🐞🐞 ValueError: split_cols failed due to a data type mismatch.")
            return df  
        try:
            split_columns = [df[col].str.split('\n', expand=True) for col in df.columns]
            result_df = pd.concat(split_columns, axis=1)
            result_df.columns = range(len(result_df.columns))
            return result_df
            df = self.split_rows(df, config=True)

            df = df.T

            # df["len"] = df.apply(lambda row: self.maxlen(row), axis=1)
            # df = df.apply(lambda row: self.normalizelists(row), axis=1)
            # df.drop(columns=['len'], inplace=True)
            # df = df.explode(df.columns.tolist()).reset_index(drop=True)
            # sorted_columns = sorted(df.columns, key=lambda x: int(x))
            # column_mapping = {current_col: index for index, current_col in enumerate(sorted_columns)}
            # df = df.rename(columns=column_mapping)
            
            # for sp in config:
            #     split_col = sp['split_col']
            #     new_cols =  sp['new_cols']
            #     pref = sp['pref']
            #     if len(new_cols)==2:df[new_cols[0]],df[new_cols[1]] = zip(*df[split_col].apply(lambda r :self.check_newlines_spilt_cols(r,pref,2)))
            #     df.drop(columns=[split_col], inplace=True)

        except Exception as e:
            print('🐞🐞Error while spliting columns: ', e)
        return df

    def merge_cols(self, df : pd.DataFrame, config:list | None = None):
        if not isinstance(config, list):
            print("🐞🐞 ValueError: merge_cols failed due to a data type mismatch.")
            return df  
        try:
            drop_cols = []
            df = df.replace('', np.nan)
            for (fc,tc) in config:
                df.iloc[:,tc] = df.iloc[:,tc].combine_first(df.iloc[:,fc])
                drop_cols.append(fc) 
            df.drop(columns=df.columns[drop_cols], inplace=True)
            df = df.replace(np.nan,'')
        except Exception as e:
            print('🐞🐞Error while merge columns: ', e)
        return df
     
    def merge_rows(self, df: pd.DataFrame, config: list | None = None):
        if not isinstance(config, list):
            print("🐞🐞 ValueError: merge_rows failed due to a data type mismatch.")
            return df

        try:
            drop_rows = []
            df = df.replace('', np.nan)

            for (fr, to) in config:
                df.iloc[to, :] = df.iloc[to, :].combine_first(df.iloc[fr, :])
                drop_rows.append(fr)

            df.drop(index=drop_rows, inplace=True)
            df = df.replace(np.nan, '')

        except Exception as e:
            print('🐞🐞Error while merge rows: ', e)

        return df

    def shift_rows(self, df: pd.DataFrame, config: list | None = None):
        if not isinstance(config, list):
            print("🐞🐞 ValueError: shift_rows failed due to a data type mismatch.")
            return df
        try:
            for skips in config:
                if "to" in skips:  # Check if 'to' is in the keys of the current skips dictionary
                    _from, _to, _skipc = skips['from'], skips['to'], skips['skip_col']
                else:
                    _from, _skipc = skips['from'], skips['skip_col']
                    _to = len(df)

                df.iloc[_from:_to, _skipc:] = df.iloc[_from:_to, _skipc:].shift(1)

        except Exception as e:
            print('🐞🐞Error occurred while shifting rows:', e)

        return df

    # def shift_col_rows(self,  df : pd.DataFrame, config:list | None = None):
    #     try:
    #         for skips in config:
    #             if "to" in skips:
    #                 _from, _to, _skipc = skips['from'], skips['to'], skips['skip_col']
    #                 df.iloc[_from:_to, _skipc:] = df.iloc[_from:_to, _skipc:].shift(1)
    #                 return df
    #             else:
    #                 _from, _skipc = skips['from'], skips['skip_col']
    #                 _to = len(df)
    #                 return df

    #     except Exception as e:
    #         print('🐞🐞Error occurred while shifting rows:', e)

    #     return df

    def remove_repeating_headers(self,  df : pd.DataFrame, config:bool | None = None):
        if not isinstance(config, bool) or config  == False:
            print("🐞🐞 ValueError: remove_repeating_headers failed due to a data type mismatch.")
            return df  
        try:
            df.columns = df.iloc[0]
            df[df.iloc[:, 0] != df.columns[0]]
        except Exception as e:
            print('🐞🐞Error while removing repeating headers: ', e)
        return df

    def remove_rows_with(self,  df : pd.DataFrame, config:list | None = None):
        if not isinstance(config, list):
            print("🐞🐞 ValueError: remove_rows_with failed due to a data type mismatch.")
            return df  
        try:
            df = df[~df.isin(config).any(axis=1)]
        except Exception as e:
            print('🐞🐞 Error while remove rows with: ', e)
        return df
    
    def add_only_rows_with(self,  df : pd.DataFrame, config:list | None = None):
        if not isinstance(config, list):
            print("🐞🐞 ValueError: remove_rows_with failed due to a data type mismatch.")
            return df  
        try:
            df = df[df.isin(config).any(axis=1)]
        except Exception as e:
            print('🐞🐞 Error while remove rows with: ', e)
        return df
    
    # def add_only_rows_with(df: pd.DataFrame, config: list | None = None, extension: str = "") -> pd.DataFrame:
    #     if not isinstance(config, list):
    #         print("🐞🐞 ValueError: add_only_rows_with failed due to a data type mismatch.")
    #         return df  
        
    #     # Add the extension to each element in the config list
    #     try:
    #         print(config)
    #         if extension:
    #             config = [item + extension for item in config]
    #             df = df[df.isin(config).any(axis=1)]
    #         else:
    #             df = df[df.isin(config).any(axis=1)]
    #     except Exception as e:
    #         print('🐞🐞 Error while adding rows with: ', e)
        
    #     return df

    def split_stat_amount(self,  df : pd.DataFrame, config:dict | None = None):
        if not isinstance(config, dict):
            print("🐞🐞 ValueError: split_stat_amount failed due to a data type mismatch.")
            return df  
        try:
            mask = df[config['ref_col']].str.contains(config['amount'])
            mask_stat = df[config['ref_col']].str.contains('|'.join(config['stat']))

            df.loc[mask, 'actual_today_debits'] = df.loc[mask, config['value_col']]
            df.loc[mask_stat, 'stat'] = df.loc[mask_stat, config['value_col']]

            df.to_csv('output.csv')

        except Exception as e:
            print('🐞🐞 Error while split_stat_amount: ', e)
        return df

    def drop_empty_cols(self, df: pd.DataFrame, config: bool  | None = None):
        # if not isinstance(config, (int, bool, type(None))):
        if not isinstance(config, bool) or config  == False:
            print("🐞🐞 ValueError: drop_col_with_empty_row failed due to a data type mismatch.")
            return df  

        try:
            # print("---------------------drop_empty_cols---------------------------")
            # print(df)
            # print("---------------------drop_empty_cols---------------------------")
            for col in df.columns:
                if (df[col].eq("") | df[col].eq("nan") | df[col].isna()).all():
                    df.drop(col, axis=1, inplace=True)
                
            if config is not None:
                df.dropna(axis=1, thresh=config, inplace=True)
                
            df.columns = range(len(df.columns))

        except Exception as e:
            print('🐞🐞Error while drop empty cols: ', e)

        return df

    def combine_rows(self, df: pd.DataFrame, config: bool | None = None) -> pd.DataFrame:
            print("config:",config)
            if not isinstance(config, bool):
                print("🐞🐞 ValueError: combine_rows failed due to a data type mismatch.")
                return df
            combined_data = []
            i = 0
            while i < len(df):
                row = df.iloc[i].tolist()
                if i < len(df) - 1 and (row[0] == "" or pd.isna(row[0])):
                    next_row = df.iloc[i + 1].tolist()
                    combined_row = [f"{a} {b}".strip() for a, b in zip(row, next_row)]
                    combined_data.append(combined_row)
                    i += 1
                else:
                    combined_data.append(row)
            
                i += 1
            df = pd.DataFrame(combined_data).fillna('')
            return df
    
    def add_lineitem_col(self,  df : pd.DataFrame):
        try:
            # print(self.lineitem_desc_label)
            # df = df.dropna(subset=[self.lineitem_desc_label], how='all')
            if 'extention' in self.__dict__:
                df['lineitem_desc'] = df[self.lineitem_desc_label].apply(lambda row: str(self.extention)+' '+str(row))
            else:
                df['lineitem_desc'] = df[self.lineitem_desc_label]
        except Exception as e:
            print('🐞🐞 Error while add_lineitem_col: ', e)
        return df
    
    def add_netAmount_col(self,  df : pd.DataFrame):
        try:
            print("-------------------------------------add_netAmount_col------------------------------------------------")
            print(df.to_string())
            if(len(self.actual_today_debits) == 1):
                df['actual_today_debits'] = df[self.actual_today_debits[0]].apply(self.format_amount)  

            elif(len(self.actual_today_debits) > 1):
                df['actual_today_debits'] = df[self.actual_today_debits[0]].apply(self.format_amount) - sum(df[x].apply(self.format_amount) for x in self.actual_today_debits[1:])

        except Exception as e:
            print('🐞🐞 Error while add_netAmount_col: ', e)
        return df

    def add_desc_col(self,  df : pd.DataFrame):
        try:
            df[self.column_headers] = df[self.columns]
        except Exception as e:
            print('🐞🐞 Error while add_lineitem_col: ', e)
        return df
        
    def Apply_PMS_Rules(self,df:pd.DataFrame, ignore_words, add_words, category, sub_category, ps_curr_stat):
        output = {'dataframe':df}
        try:
            
            # print('--------------------------RAW DF------------------------')
            # print(df.to_string())
            # # print(tabulate(df, headers='keys', tablefmt='simple_grid', maxcolwidths=10))
            # print('--------------------------RAW DF------------------------')

            if self.submission_type != False:
                output['submission_type'] = self.submission_type

            if not df.empty:
                df = df[~df.isin(ignore_words).any(axis=1)]
                if add_words:    
                    df = df[df.isin(add_words).any(axis=1)]
                # if add_contains:
                #     df = df[df.isin(add_contains).any(axis=1)]
                # print("---------------------------------------category-----------------------------------------------------------")
                # print(category)
                # print("-------------------------------------------category-------------------------------------------------------")
                
                if category:
                    if self.cn1:
                        df[self.cn1] = category
                    else:
                        df['category'] = category
                if sub_category:
                    if self.cn2:
                        df[self.cn2] = sub_category
                    else:
                        df['sub_category'] = sub_category
                if ps_curr_stat:
                    if self.cn3:
                        df[self.cn3] = ps_curr_stat
                    else:
                        df['ps_curr_stat'] = ps_curr_stat
                
                # if category:
                #     df[self.cn1] = category
                # if sub_category:
                #     df[self.cn2] = sub_category
                # if ps_curr_stat:
                #     df[self.cn3] = ps_curr_stat
#                 for col in df.columns:
#                     if (df[col].eq("") | df[col].eq("nan") | df[col].isna()).all():
#                         df.drop(col, axis=1, inplace=True)
# # 
#                 df.columns = range(len(df.columns))

                if self.lineitem_desc_label or self.lineitem_desc_label == 0:
                    df = self.add_lineitem_col(df)

                if self.column_headers or self.columns == 0:
                    df = self.add_desc_col(df)

                if self.actual_today_debits !=False:
                    df = self.add_netAmount_col(df)
                    
                if self.adjusted_credits != False:
                    df['adjusted_credits'] = df[self.adjusted_credits]

                if self.net_amount != False:
                    df['net_amount'] = df[self.net_amount]
                    
                if self.stat != False:
                    df['stat'] = df[self.stat]

                df = df.fillna('')
                
                print('--------------------------Final DF------------------------')
                # print(df.to_string())
                print(tabulate(df, headers='keys', tablefmt='simple_grid', maxcolwidths=15))
                print('--------------------------Final DF------------------------')

                df.to_csv('syn2.csv')
                # clean_records = [{k: v for k, v in record.items() if v is not None} for record in df.to_dict(orient='records')]
                # df = pd.DataFrame(clean_records)
                # print("--------------------------------clean_records--------------------------------------------------")
                # # print(df.to_string())
                # print(tabulate(df, headers='keys', tablefmt='simple_grid', maxcolwidths=15))
                # # print(clean_records)
                # print("---------------------------------clean_records-------------------------------------------------")
                output['dataframe'] = df.to_dict(orient='records')
                # print(output)   
                return output       
            
            else:
                return output
        except Exception as ex:
            print('🐞🐞 Error in Apply_PMS_Rules', ex)
            return output
    
    def triggers(self,  df : pd.DataFrame, config:list | None = None):
        if not isinstance(config, list) or len(config) == 0:
            print("🐞🐞 ValueError: triggers failed due to a data type mismatch.")
            data = self.Apply_PMS_Rules(df, [])
            return [data]
        try:
            dfs_ids=[]
            df[self.ref_col]=df[self.ref_col].apply(lambda r:str(r).replace('\n','').strip())
            for idx,tr in enumerate(config):
                if 'ignore_words' not in tr.keys():
                    tr['ignore_words'] = []
                if 'add_words' not in tr.keys():
                    tr['add_words'] = []
                if 'category' not in tr.keys():
                    tr['category'] = []
                if 'sub_category' not in tr.keys():
                    tr['sub_category'] = []
                if 'ps_curr_stat' not in tr.keys():
                    tr['ps_curr_stat'] = []
                self.extention = tr['extension']
                if idx+1 <= len(config) and 'end' in tr:
 
                    if (df[self.ref_col]== tr['start']).any():
                        start_index = df[df[self.ref_col] == tr['start']].index.max()
                    else:
                        start_index = None

                    if (df[self.ref_col] == tr['end']).any():
                        end_index = df[df[self.ref_col] == tr['end']].index.max()
                    else:
                        end_index = None

                    if start_index != None and end_index != None:
                        res= self.Apply_PMS_Rules(df[ start_index:end_index], tr['ignore_words'],tr['add_words'], tr['category'], tr['sub_category'], tr['ps_curr_stat'])
                        dfs_ids.append(res)
                    # else:
                    #     res=self.Apply_PMS_Rules(df[ start_index:], tr['ignore_words'])    
                    elif start_index != None and end_index == None:
                        res=self.Apply_PMS_Rules(df[ start_index:], tr['ignore_words'], tr['add_words'], tr['category'], tr['sub_category'], tr['ps_curr_stat'])
                        dfs_ids.append(res)
                    
                else:
                    if (df[self.ref_col] == tr['start']).any():
                        start_index = df[df[self.ref_col] == tr['start']].index.max()
                    else:
                        start_index = None

                    if start_index != None:
                        res=self.Apply_PMS_Rules(df[ start_index:], tr['ignore_words'], tr['add_words'], tr['category'], tr['sub_category'], tr['ps_curr_stat'])
                        dfs_ids.append(res)
            
            return dfs_ids
        
        except Exception as e:
            print('🐞🐞 Error while triggers: ', e)
            return [df]
  
def preInitiateExePre(df, config):
    return DataFramePreparation(config).process_dataframe(df, config)

with open('temp.json', 'r') as data_file:
    config: dict = json.load(data_file)

# file = "C:\\Users\\User1\\Downloads\\new\\ONQ EXCEL\\20240305-d1780dc8-9f09-4c83-b7ba-192ce45312c3.xls"
# file = "C:\\Users\\User1\\Downloads\\20240619061051887671-20240607061759000000-1_Final Audit (1)\\tables\\fileoutpart7.xlsx"
# # file = "D:\\S_Path\\Vss_Repo\\pandas\\Dataframe_Extraction_Service_API\\Version_1\\DataframePreprocessing\\Tools\\pdfFormat\\Adobe\\archive_files\\20240619191244750038-20240607061759000000-3_Final Audit (3)\\tables\\fileoutpart6.xlsx"
# file = "C:\\Users\\User1\\Downloads\\20240706070925747062-20240530123507000000-7_rvyacctg.pdf052424\\tables\\fileoutpart6.xlsx"
# file = "D:\\OLD APPS\\Test\\Repository\\Pending\\redistay\\New folder\\feb\\01\\HOTEL LEDGER COMPARISON 2-1-2024_.xls"
# file = "D:\\NEW CHANGES\\ANANDSYSTEMS\\DailySummaryReport_17577 (6).xls"
file = "D:\\NEW CHANGES\\ANANDSYSTEMS\\Ledger Summary - Daily_17577 (6).xls"

# fname, ext = os.path.splitext(os.path.basename(file))

try:
    df = pd.read_excel(file, header=None)  
except:    
    try:
        # df = pd.read_excel(file, header=None)
        df = pd.read_csv(file,  header=None, delimiter="\\t")
    except:
        try:
            df = pd.read_excel(file, header=None, engine='python')
            # df = pd.read_csv(file,  header=None, delimiter="\t")
        except:
            df = pd.read_excel(file, header=None, engine='xlrd')


# print("--------------------------start--------------------------------------")
#     df = pd.read_excel(file, header=None, engine='xlrd')
# except:
#     try:
#         print("----------------------delimiter-------------------------------")
#         df = pd.read_csv(file, header=None, delimiter='\\t')
#     except:
#         print("----------------------engine------------------------------------")
#         df = pd.read_csv(file, header=None)
print(df.to_string())
# df = pd.read_csv(file,  header=None)
# print(df.to_dict(orient='records'))
# df = df.apply(lambda x: x.str.replace(' _x000D_', ''))
# print(df.to_dict(orient='records'))
# print(df)
# df = df.apply(lambda x: x.str.replace(' _x000D_', ''))
# df = df.apply(lambda x: x.str.replace('_x000D_', ''))
# print(df.to_dict(orient='records'))
# # print(df)
# dfs = df.apply(lambda x: x.strip() if isinstance(x, str) else x)
# print(df.to_dict(orient='records'))
# print(df)

# df = df.apply(lambda x: x.str.replace('\t', '')) 
# preInitiateExePre(df, config[0]) 

# #
# input_pdf = "D:\\OLD APPS\\Test\\Repository\\Pending\\Autoclerk\\Feb\\23\\tranSummary_2024-02-23.pdf"
# # input_pdf = "D:\\OLD APPS\\Test\\Repository\\Done\\cloudbed\\feb\\24\\Report_1708981347180.pdf"
# # input_pdf = "D:\\OLD APPS\\Test\\Repository\\PMS reports.1\\5 STAR\\March1stStats.pdf"
# input_pdf = 'C:\\Users\\User1\\Downloads\\DailyReport-1.pdf'
# input_pdf = "C://Users//raju.kotyada//Downloads//pms//pms//HOTELKEY//Final Audit (22).pdf"
# input_pdf = "C:\\Users\\raju.kotyada\\Downloads\\pms\\pms\\opera\\13march\\stat_dmy_seg5839625.pdf"
# input_pdf = "C:\\Users\\raju.kotyada\\Downloads\\pms\\pms\\opera\\13march\\trial_balance5839630.pdf"
# input_pdf = "D:\\OLD APPS\\Test\\Repository\\Done\\CHOICE\\05\\report - 2024-03-06T101151.034.pdf"
# # input_pdf = "D:\\OLD APPS\\Test\\Repository\\pms\\msi\\07\\Daily activity report 3-7-2024.pdf"
# input_pdf = "C:\\Users\\raju.kotyada\\Downloads\\synxis\\synxis\\23\\sphStatistics (19).pdf"

# tables = cam.read_pdf(input_pdf, pages="all", flavor='stream', edge_tol=500)
# # tables = cam.read_pdf(input_pdf, pages="all", flavor='stream')
# for table in tables:
#     df: pd.DataFrame = table.df
#     print('----------------------------------RAW DF-----------------------------------')
#     print(df)
#     print('----------------------------------RAW DF-----------------------------------')
#     output = preInitiateExePre(df, config[0])
#     # print(output)
    
