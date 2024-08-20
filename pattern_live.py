import re,os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from re import sub
from decimal import Decimal
from tabulate import tabulate

class PatternBased_DfPrepartionTool:
    def __init__(self,pattern,filename,head,lineitem_desc_label,today_actual_debits_label) -> None:
        # print("-------------------------------------------pattern-----------------------------------------------------------")
        # print(pattern)
        # print("-------------------------------------------pattern-----------------------------------------------------------")
        # print(filename)
        # print(head)
        # print(lineitem_desc_label)
        # print(today_actual_debits_label)
        self.data={}
        self.trigger = False
        self.ref = False
        self.lineitem_desc_label=lineitem_desc_label
        self.today_actual_debits_label=today_actual_debits_label
        self.head = head
        self.pattern_Start = pattern['start_seq']
        self.pattern_End = pattern['end_seq']
        self.filename =  filename
        self.lineitem_position = 0 #int(pattern['lineitem_position'])
        self.ignore_words = pattern['ignore_words']
        self.commenExtension = pattern['commonExtensions']
        self.triggers_list = pattern['triggers']
        self.submission_type = pattern['submission_type']
        self.pattern = pattern



        #-----------------------------------------

        load_dotenv()
        db_url = os.getenv('db_url')
        cluster = MongoClient(db_url)
        db_name = os.getenv('db_name')
        self.db = cluster[db_name]
        self.linedescriptionLmt =0
        self.dfs_ids = []
        self.file_Date=''
        self.facility_id=''


    def get_start_end_idx(self,index,line):
        i = index
        while i >= 0 and line[i] != '  ':
            i -= 1
        start_index = i + 1
        # Search forward for the space character
        i = index
        while i < len(line) and line[i] != '  ':
            i += 1
        end_index = i
        # Extract the value
        value = line[start_index:end_index]
        # parts = line.split('  ')
        # value = parts[index]

    def find_matches(self,string,line):
        pattern=''
        for index,c in enumerate(string.strip().split(' ')):
            if index==len(string.strip().split(' '))-1:
                pattern+=c
            else:pattern+=c+'\s*'
        matches = re.search(pattern, line)
        newline = line[:matches.start()] + string+ line[matches.end()+1:]
        return newline
    
    def is_number(self,string):
        pattern = r'^[+-]?\d{1,3}(,\d{3})*(\.\d+)?$'
        match = re.match(pattern, string)
        return bool(match)

    def contains_alpha_or_special(self,string):
        pattern = r'[a-zA-Z!@#$%^&*()]'
        match = re.search(pattern, string)
        return match is not None

    def check_line_arr(self,line_arr,line):
        fin_arr=[]
        temp_arr = []
        for index,item in enumerate(line_arr):
            if index ==self.lineitem_position:
                if self.is_number(item.strip()) or item.strip() =='.00' or self.contains_alpha_or_special(item.strip())==False:
                    temp_arr.append(item)
                else:
                    if self.lineitem_position !=0 and int(self.lineitem_position)-1 in temp_arr:
                        temp_arr[int(self.lineitem_position)-1] = str(temp_arr[int(self.lineitem_position)-1].strip()+' '+item)
                        if not self.is_number(item.strip()):
                            rpstr = self.find_matches(temp_arr[int(self.lineitem_position)-1],line)
                            line =rpstr
                    else:
                        temp_arr.append(item)
            else:temp_arr.append(item)
        
        for item in temp_arr:
            if '.00' in item :
                item_sp=(item.strip().split(' '))
                for i in item_sp:
                    fin_arr.append(i)

            else:
                fin_arr.append(item)
        return [fin_arr,line]

    def format_amount(self,t):
        try:
            if t == '':
                return 0
            # d = Decimal(sub(r'[^\d.]','',t))
            d = Decimal(sub(r'[^\d.-]', '', t))
            if t.find("(") >= 0 or t.find(")") >= 0:
                d = -d
            return float(d)
        except:
            if(self.is_number(str(t).strip()) or str(t).strip() =='.00' or self.contains_alpha_or_special(str(t).strip())==False):
                return t
            else:return 0
    
    def format_sign(self,t,ref):
        try:
            if ref=='negative':return float(-t)
            elif ref =='positive':return float(+t)
            else:return float(t)
        except: return t

    def get_value(self,line,trgs):
        _line_arr = list(filter(lambda x: x != '' ,line.split('  ')))
        line_arr,line=self.check_line_arr(_line_arr,line)
        start_index = 0
        end_index = 0
        final_line_arr=[]
        for index,l in enumerate(line_arr):
            if index==0:
                final_line_arr.append(l)
                start_index = line.index(l,end_index)
                end_index = start_index+len(l)

            else:
                if index==self.lineitem_position:
                    ref_count=self.linedescriptionLmt
                    ignore_index=end_index
                    sub_index= start_index
                else:
                    ref_count=14
                    ignore_index = end_index
                    sub_index=end_index
                if l in line and line.index(l,ignore_index)-sub_index <= ref_count:
                    final_line_arr.append(l)
                    start_index = line.index(l,end_index)
                    end_index = start_index+len(l)

                else:
                    final_line_arr.append('')
                    final_line_arr.append(l)
                    start_index = line.index(l,end_index)
                    end_index = start_index+len(l)
        if 'merge_rows' in self.pattern:
            for mr in self.pattern['merge_rows']:
                mr_idx1 = mr[0]
                mr_idx2 = mr[1]

            if len(final_line_arr)> mr_idx1 and len(final_line_arr)>mr_idx2:
                merge_element = final_line_arr[mr_idx1]+' '+final_line_arr[mr_idx2]
                final_line_arr = final_line_arr[:mr_idx1] + [merge_element] + final_line_arr[mr_idx2 + 1:]

        if (len(final_line_arr)==len(self.data)):
            return final_line_arr
        else:
            filtered_data = [item for item in final_line_arr if item != '']
            if(len(filtered_data)==len(self.data)):
                return filtered_data
            else:
                if(len(final_line_arr)==len(self.data)-1):
                    final_line_arr.append('')
                    return final_line_arr
                else:
                    if trgs != None and trgs['start_line_no']==trgs['end_line_no']:
                        if(len(filtered_data)+1==len(self.data)):
                            filtered_data.insert(0,'-  ')
                            return filtered_data

    def has_matching_pattern(self,words, line):
        # print('word',words)
        # print('line-------------',line)
        return any(word.lower() in [l.lower() for l in line.split("  ")] for word in words)
        # return any(re.search(pattern=word.lower(),string=line.lower(),flags=re.DOTALL) for word in words)

    def get_key(self,key):
        if key in self.data:
            if self.cls in key.split('_'):
                self.cls_list.pop(0)
                self.cls = self.cls_list[0]
                key =  (''.join([element for index, element in enumerate(key.split('_')) if index != 0])).strip()
            newkey = self.cls+'_'+str(key)
            return self.get_key(newkey)
        else:
            return key
   
    def replace_multiple_spaces(self,text):
        return re.sub(r'\s+', ' ', text)

    def process_line(self,line,add_line,trgs):
        patterns = [ self.pattern_Start, self.pattern_End  ]
        for index, pattern in enumerate(patterns):
            linedescriptionLmt_match = re.search(self.lineitem_desc_label.replace(' ','\s+'), line)
            if linedescriptionLmt_match is not None:
                self.linedescriptionLmt= linedescriptionLmt_match.end()
            block = re.search(pattern=pattern,string=self.replace_multiple_spaces(line),flags=re.DOTALL)
            if block is not None:
                if index==0 and self.ref ==False:
                    # if len(self.data)>0:
                    #     df = pd.DataFrame(self.data)
                    #     df = df.reset_index(drop=True)
                    #     self.Apply_PMS_Rules(df)

                    self.data={}
                    self.cls_list = list(self.commenExtension)# ['ptd','ytd']
                    self.cls=self.cls_list[0]#'ptd'
                    header_labels = list(filter(lambda x: x != '', line.split('  ')))
                    for index,h in enumerate(header_labels):
                        key = self.get_key(h.strip())
                        if 'split_col_heads' in self.pattern:
                            for hd in self.pattern['split_col_heads']:
                                mt = re.search(pattern=hd['split_head'],string=key,flags=re.DOTALL)
                                if mt is not None:
                                    newkey1 = self.get_key(key.split(hd['split_with'])[0].strip())
                                    newkey2 = self.get_key(hd['split_with'])
                                    self.data[newkey1]=[]
                                    self.data[newkey2]=[]
                                    if newkey1 == self.lineitem_desc_label:self.lineitem_position=index
                                    elif newkey1 == self.lineitem_desc_label:self.lineitem_position=index+1
                                    break

                                else:self.data[key]=[]
                        else:self.data[key]=[]
                        if key == self.lineitem_desc_label:self.lineitem_position=index
                    self.ref = True

                    return
                elif index==1 and add_line:
                    if re.search(pattern=r"\.00",string=line,flags=re.DOTALL) is not None:
                        values= self.get_value(line,trgs)
                        if values and (len(values)==len(self.data)):self.ref=True
                        else:self.ref= False

                    return

        if self.ref and add_line:
            
            if re.search(pattern=r"\.00",string=line,flags=re.DOTALL) is not None:
                values= self.get_value(line,trgs)
                if self.has_matching_pattern(self.ignore_words,line)  :
                    # print('ignore match',values)
                    return
                if 'add_only_rows_with' in self.pattern and self.has_matching_pattern(self.pattern['add_only_rows_with']) == False:
                    return
                        

                if self.lineitem_position=='0':check_lineitem_position = 1
                else:check_lineitem_position=self.lineitem_position
                if values and (len(values)==len(self.data)) and values[check_lineitem_position] !='' :
                    for i,item in enumerate(values):
                        keys_list = list(self.data.keys())
                        _key = keys_list[i]
                        self.data[_key].append(item)

    def format_desc(self,row,ref):
        try:return str(row)+' '+str(ref)
        except:return row

    def Apply_PMS_Rules(self,df):
        # print('------------------PRE-----------------------------------')
        # print(df.to_string())
        # print('------------------PRE-----------------------------------')
        output = {'dataframe':df.to_dict(orient='records')}
        try:
            if self.submission_type != False:
                output['submission_type'] = self.submission_type

            if not df.empty:
                if 'ref' in self.pattern:df['lineitem_desc'] = df[self.lineitem_desc_label].apply(lambda row: self.format_desc(row,self.pattern['ref']))
                else:df['lineitem_desc'] = df[self.lineitem_desc_label]

                if 'columns' in self.pattern:
                    df[self.pattern['column_headers']] = df[self.pattern['columns']]
                
                if 'category' in self.pattern:
                    df['category'] = self.pattern['category']
                    
                if 'sub_category' in self.pattern:
                    df['sub_category'] = self.pattern['sub_category']
                
                if 'ps_curr_stat' in self.pattern:df['ps_curr_stat'] = self.pattern['ps_curr_stat']
                if(len(self.today_actual_debits_label)==1):
                        df['today_actual_debits'] = df[self.today_actual_debits_label[0]].apply(self.format_amount)
                elif(len(self.today_actual_debits_label)>1):
                    df['today_actual_debits'] =df[self.today_actual_debits_label[0]].apply(self.format_amount) - sum(df[x].apply(self.format_amount) for x in self.today_actual_debits_label[1:])
                
                if 'adjusted_credits_label' in self.pattern:df['adjusted_credits'] = df[self.pattern['adjusted_credits_label']]
                # if(len(self.adjusted_credits_label)==1):
                #     df['adjusted_credits'] = df[self.adjusted_credits_label[0]].apply(self.format_amount)

                if 'stat' in self.pattern:df['stat'] = df[self.pattern['stat']]
                

                if 'ref_sign' in self.pattern:df['today_actual_debits'] = df['today_actual_debits'].apply(lambda row: self.format_sign(row,self.pattern['ref_sign']))
                if 'ref_sign' in self.pattern:df['adjusted_credits'] = df['adjusted_credits'].apply(lambda row: self.format_sign(row,self.pattern['ref_sign']))

                # df.to_csv(f"res.csv", index=False, encoding='utf-8')0
                print('-------------------------final df ------------------------------')
                print(df.to_string())
                # print(tabulate(df, headers='keys', tablefmt='simple_grid', maxcolwidths=15))
                print('-------------------------final df ------------------------------')
                output['dataframe'] = df.to_dict(orient='records')
                # print(output)
                return output
            else:return output
        except Exception as ex:
            print(ex)
            return output

    def find_lines_with_pattern(self,filename, pattern):
        pattern = pattern.split('\\n')
        st = 0
        with open(filename,'r') as NF:
            for i,f in enumerate(NF):
                _line_arr = list(filter(lambda x: x != '' ,f.strip().split('  ')))
                if(re.search(pattern=pattern[0],string=f,flags=re.DOTALL) is not None) or pattern[0]=='\\t' and len(_line_arr)==0:
                    st=1
                    if len(pattern) == 1:return i
                    else:continue
                if st==1:

                    if len(_line_arr)>0 and _line_arr[0].strip()==pattern[1].strip():
                        return i
                    else:st=0
        return ''

    def run(self,f,trgs):
        for idx,line in enumerate(f):
            if trgs['start_line_no'] !='' and trgs['end_line_no']!='':
                if idx==trgs['start_line_no']==trgs['end_line_no']: add_line =True
                elif(idx>=trgs['start_line_no'] and idx< trgs['end_line_no']):add_line =True
                elif idx> trgs['end_line_no']:
                    add_line = False
                    break
                else:add_line = False
                self.process_line(line.strip(),add_line,trgs)

    def startPreparation(self):
        match_heads = []
        with open(self.filename,'r') as F:
            if(re.search(pattern=self.head,string=F.read(),flags=re.DOTALL) is not None):
                match_heads.append(self.head)
                if len(self.triggers_list)>0:
                    for trg in self.triggers_list:
                        with open(self.filename,'r') as f:
                            trg['start_line_no'] = self.find_lines_with_pattern(self.filename,trg['start'])
                            trg['end_line_no'] = self.find_lines_with_pattern(self.filename,trg['end'])
                            self.run(f,trg)

                else:
                    with open(self.filename,'r') as f:
                        for idx,line in enumerate(f):
                            self.process_line(line.strip(),True,None)
            else:print('Header not found')

        dfl= pd.DataFrame(self.data)
        # print(self.data)
        res = self.Apply_PMS_Rules(dfl)
        # print("-----------------------------------------------------startPreparation--------------------------------------------------")
        # print(res)
        # print("-----------------------------------------------------startPreparation--------------------------------------------------")
        return [[res],match_heads]
    
    
pms = 'fosse'
# filename = r'D:\\FOSSE\\7\\D A I L Y   C L O S I N G   R E P O R T-7thjuly.txt'
filename = r'D:\\FOSSE\\7\\Daily Segmentation Report-8thjuly.txt'

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
    if obj['type'] == 'pattern':
        for pattern in obj['patterns']:
            if 'lineitem_desc_label' in pattern:
                initiate = PatternBased_DfPrepartionTool(pattern,filename,obj['head'],pattern['lineitem_desc_label'],pattern['today_actual_debits_label'])
                # print("--------------------------initiate------------------------------")
                # # print(initiate)
                # print("--------------------------initiate------------------------------")
                initiate.startPreparation()
            else:
                print("--------------------------head------------------------------")
                print(obj['head'])
                print("--------------------------head------------------------------")

    # def preInitiate(pattern,filename,head,lineitem_desc_label,today_actual_debits_label):
    #     initiate = PatternBased_DfPrepartionTool(pattern,filename,head,lineitem_desc_label,today_actual_debits_label)
    #     print("-----------------------------------res-----------------------------------------")
    #     res = initiate.startPreparation()   
    #     print(res)
    #     print("----------------------------------res------------------------------------------")

    #     return res