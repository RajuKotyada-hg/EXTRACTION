import pandas as pd
import re,os,json
from re import sub
from decimal import Decimal
from pymongo import MongoClient
from inspect import currentframe, getframeinfo

class KeywordBased_DfPreparation:
    def __init__(self,cfg,filename) -> None:
        self.keywords = cfg['keywords']
        self.head = cfg['head']
        self.submission_type = cfg['submission_type']
        self.ignore_words = cfg['ignore_words']
        self.Value_type = cfg['Value_type']
        
        self.filename = filename
        self.ref = False
        self.data = {}
        self.results = []

    def check_ignore_words(self,_line_arr):
        if len(self.ignore_words)>0:
            ig_keys = list(filter(lambda x: x==_line_arr[0],self.ignore_words))
            if(len(ig_keys)>0):return False
            else:return True
        else: return True

    def contains_alpha_or_special(self,string):
        pattern = r'[a-zA-Z!@#$%^&*()]'
        match = re.search(pattern, string)

        return match is not None
    
    def format_amount(self,t):
        try:
            if(t[-1]=='-'):t='-'+t[:-1]
            if t == '' or self.contains_alpha_or_special(t.strip()):
                return 0
            # d = Decimal(sub(r'[^\d.]','',t))
            
            d = Decimal(sub(r'[^\d.-]', '', t))
            if t.find("(") >= 0 or t.find(")") >= 0:
                d = -d
            return float(d)
        except Exception as ex:
            if(self.is_number(t.strip()) or t.strip() =='.00' or self.contains_alpha_or_special(t.strip())==False):
                return t
            else:return 0

    def is_number(self,string):
        if(string[-1]=='-'):string=string[:-1]
        if self.contains_alpha_or_special(string.strip()):return False
        pattern = r'^[+-]?\d{1,3}(,\d{3})*(\.\d+)?$'
        try:
            S = str(Decimal(sub(r'[^\d.]','',string)))
            return True
        except Exception as e:
            match = re.match(pattern, string.strip())
            print("------------------------------------------match----------------------------------------------------")
            print(match)
            print("-------------------------------------------match---------------------------------------------------")
            if not bool(match):
                if string.strip()=='.00' or string.strip()=='0.00':
                    return True
            return bool(match)  
    
    def process_line(self,line,patterns,ref,kws):
        for index, pattern in enumerate(patterns):
            block = re.search(pattern=pattern,string=line,flags=re.DOTALL)
            if block is not None:
                
                if index == 0:
                    if len(self.data)>0:
                        self.ref=True
                    if self.Value_type=='stat':self.data = {'lineitem_desc':[],'stat':[]}
                    else:self.data = {'lineitem_desc':[],'net_Amount':[]}
                    self.ref=True
                    return
                elif index == 1: 
                    self.ref= False
                    if len(self.data)>0:
                        self.ref=True
                        df = pd.DataFrame(self.data)
                        print("-----------------------self.data----------------------------------")
                        print(self.data)
                        print("------------------------self.data----------------------------------")
                        df = df.reset_index(drop=True)
                        # if 'imp_words' in kws:
                        #     print('************************')
                        #     print(df)
                        #     print('************************')
                        #     # df = df[df.isin(kws["imp_words"]).any(axis=1)] 
                        #     df=df[df['lineitem_desc'].str.contains('|'.join(kws['imp_words']), case=False)]
                        if 'ignore_words' in kws:
                            # df = df[~df.isin(kws["ignore_words"]).any(axis=1)]
                            df=df[~df['lineitem_desc'].str.contains('|'.join(kws['ignore_words']), case=False)]
                        print(f'-------------------------final df {self.submission_type} ------------------------------')
                        print(df.to_string())
                        print('-------------------------final df ------------------------------')
                        output = {'dataframe':df.to_dict(orient='records')}
                        print('-------------------------output df ------------------------------')
                        print(output)
                        print('-------------------------final df ------------------------------')
                        if self.submission_type != False:
                            output['submission_type'] = self.submission_type
       

                        
                        self.results.append(output)
                        # if not df.empty:
                        #     res=self.db.dfms.insert_one({
                        #         'dataframe':data,
                        #         'submission_type':self.submission_type
                        #     })

                    if self.Value_type=='stat':self.data = {'lineitem_desc':[],'stat':[]}
                    else:self.data = {'lineitem_desc':[],'net_Amount':[]}
                    return 
                    
        if self.ref:
            matches = [(element, line.find(element)) for element in kws['imp_words']]
            matches = [(element, index) for element, index in matches if index != -1]
           
            if(len(matches)>0):
                line_start = matches[0][1]
                new_line = line[line_start:]
                _line_arr = list(filter(lambda x: x != '' ,new_line.split('  ')))
                print("-------------------------------_line_arr---------------------------------------")
                print(_line_arr)
                print("-------------------------------_line_arr---------------------------------------")
                
                if len(_line_arr)> 0 and _line_arr[0] != patterns[0]:
                    # if self.check_ignore_words(_line_arr) and len(_line_arr)>1:
                    if  len(_line_arr)>1:
                        desc = re.sub(r'[^a-zA-Z0-9\s]', ' ', _line_arr[0].strip())
                        if 'amount_position' in kws:
                            idx = kws['amount_position']
                            if kws['amount_position']<len(_line_arr):
                                
                                if  self.is_number(_line_arr[idx]):
                                    self.data['lineitem_desc'].append(ref+' '+desc)
                                    if self.Value_type=='stat':self.data['stat'].append(self.format_amount(_line_arr[idx].strip()))
                                    else:self.data['net_Amount'].append(self.format_amount(_line_arr[idx].strip()))
                                elif len(_line_arr)>2 and self.is_number(_line_arr[2]):
                                    self.data['lineitem_desc'].append(ref+' '+desc)
                                    if self.Value_type=='stat':self.data['stat'].append(self.format_amount(_line_arr[2].strip()))
                                    else:self.data['net_Amount'].append(self.format_amount(_line_arr[2].strip()))
                                # else:
                                #     print(line,len(_line_arr)>2 , self.is_number(_line_arr[2]),_line_arr)
                            else:
                                self.data['lineitem_desc'].append(ref+' '+desc)
                                if self.Value_type=='stat':self.data['stat'].append(self.format_amount(_line_arr[1].strip()))
                                else:self.data['net_Amount'].append(self.format_amount(_line_arr[1].strip()))
                        
                        elif self.is_number(_line_arr[1]) and 'amount_position' not in kws:
                            self.data['lineitem_desc'].append(ref+' '+desc)
                            if self.Value_type=='stat':self.data['stat'].append(self.format_amount(_line_arr[1].strip()))
                            else:self.data['net_Amount'].append(self.format_amount(_line_arr[1].strip()))
                            
                        else:
                            if len(_line_arr)>2 and self.is_number(_line_arr[2]):
                                self.data['lineitem_desc'].append(ref+' '+desc)
                                if self.Value_type=='stat':self.data['stat'].append(self.format_amount(_line_arr[2].strip()))
                                else:self.data['net_Amount'].append(self.format_amount(_line_arr[2].strip()))
                                                                       
    def startPreparation(self):
        matched_heads=[]
        with open(self.filename,'r') as F:

            if(re.search(pattern=self.head,string=F.read(),flags=re.DOTALL) is not None) :
                matched_heads.append(self.head)
                for kws in self.keywords:
                    patterns = [ kws['start'], kws['end']  ]
                    with open(self.filename,'r') as f:
                        for line in f:
                            self.process_line(line.strip(),patterns,kws['ref'],kws)
            else:
                print('header not found',self.head)
        return [self.results,matched_heads]

    # def preInitiate(cfg,filename):
    #     # print("----------------------cfg-------------------------------")
    #     # print(cfg)
    #     initiate = KeywordBased_DfPreparation(cfg,filename)
    #     # print("-----------------------filename------------------------------")
    #     # print(filename)
    #     # print("-------------------------filename----------------------------")
    #     # print(initiate)
    #     # print("--------------------------initiate---------------------------")


    #     res= initiate.startPreparation()
    #     return res
    
pms = 'fosse'
# filename = r'D:\\FOSSE\\7\\D A I L Y   C L O S I N G   R E P O R T-7thjuly.txt'
filename = r'D:\\FOSSE\\7\\D A I L Y   C L O S I N G   R E P O R T   S U M M A R Y-7thjuly.txt'

# filename = r'D:\\configfiles\\PMS REPORTS Day-3\\TEXT\\fossie\\HjInMxMsWUu5oCHmHgfISAM102Apr23.txt'
# filename = r'D:\\configfiles\\PMS REPORTS Day-3\\TEXT\\fossie\\be0PYEPvW02O6mmNc36zkgOPTRR102Apr23.txt'

# \\lightspeedcpltd\\20230912_DAILYR_203071.txt'

db_url = 'mongodb://localhost:27017'
cluster = MongoClient(db_url)
db_name = 'my_config_db'
db = cluster[db_name]
# print(db)
config = list(db.fosee.find({"pms":pms}))
for obj in config[0]['reportHeads']:
    # print(obj)
    # print(config[0]['reportHeads'])
    # if obj['type'] == 'impkeywords':
    #     for impkeywords in obj['keywords']:
    #         print(obj)
        # if 'lineitem_desc_label' in impkeywords:
        #     print(config)
    initiate = KeywordBased_DfPreparation(obj,filename)
    # print("--------------------------initiate------------------------------")
    # # print(initiate)
    # print("--------------------------initiate------------------------------")
    initiate.startPreparation()
else:
    print("--------------------------head------------------------------")
    print(obj['head'])
    print("--------------------------head------------------------------")