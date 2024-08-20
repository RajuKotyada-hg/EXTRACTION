import pandas as pd
import re
import json
from decimal import Decimal
from dotenv import load_dotenv
from pymongo import MongoClient
from re import sub
import os

class DataPreparationTool:
    def __init__(self, cfg, filename):
        # Configuration attributes
        self.keywords = cfg.get('keywords', [])
        self.head = cfg.get('head', '')
        self.submission_type = cfg.get('submission_type', False)
        self.ignore_words = cfg.get('ignore_words', [])
        self.Value_type = cfg.get('Value_type', 'stat')

        # File and data attributes
        self.filename = filename
        self.ref = False
        self.data = {}
        self.results = []

        # Pattern attributes
        self.pattern = cfg.get('pattern', {})
        self.lineitem_desc_label = self.pattern.get('lineitem_desc_label', '')
        self.net_Amount_label = self.pattern.get('net_Amount_label', [])
        self.pattern_Start = self.pattern.get('start_seq', '')
        self.pattern_End = self.pattern.get('end_seq', '')
        self.lineitem_position = 0
        self.linedescriptionLmt = 0

        # MongoDB setup
        load_dotenv()
        db_url = os.getenv('db_url')
        cluster = MongoClient(db_url)
        db_name = os.getenv('db_name')
        self.db = cluster[db_name]

    def check_ignore_words(self, _line_arr):
        return not any(word == _line_arr[0] for word in self.ignore_words)

    def contains_alpha_or_special(self, string):
        return bool(re.search(r'[a-zA-Z!@#$%^&*()]', string))

    def format_amount(self, t):
        try:
            if t[-1] == '-':
                t = '-' + t[:-1]
            if not t or self.contains_alpha_or_special(t.strip()):
                return 0
            d = Decimal(sub(r'[^\d.-]', '', t))
            if '(' in t or ')' in t:
                d = -d
            return float(d)
        except Exception as ex:
            if self.is_number(t.strip()) or t.strip() == '.00' or not self.contains_alpha_or_special(t.strip()):
                return t
            else:
                return 0

    def is_number(self, string):
        if string[-1] == '-':
            string = string[:-1]
        if self.contains_alpha_or_special(string.strip()):
            return False
        try:
            Decimal(sub(r'[^\d.]', '', string))
            return True
        except:
            return bool(re.match(r'^[+-]?\d{1,3}(,\d{3})*(\.\d+)?$', string.strip()))

    def find_matches(self, string, line):
        pattern = re.sub(r'\s+', r'\s*', string.strip())
        matches = re.search(pattern, line)
        return line[:matches.start()] + string + line[matches.end()+1:]

    def check_line_arr(self, line_arr, line):
        fin_arr, temp_arr = [], []
        for index, item in enumerate(line_arr):
            if index == self.lineitem_position:
                if self.is_number(item.strip()) or item.strip() == '.00' or not self.contains_alpha_or_special(item.strip()):
                    temp_arr.append(item)
                else:
                    if self.lineitem_position != 0 and int(self.lineitem_position)-1 in temp_arr:
                        temp_arr[int(self.lineitem_position)-1] += f' {item}'
                        if not self.is_number(item.strip()):
                            line = self.find_matches(temp_arr[int(self.lineitem_position)-1], line)
                    else:
                        temp_arr.append(item)
            else:
                temp_arr.append(item)
        
        for item in temp_arr:
            if '.00' in item:
                fin_arr.extend(item.strip().split(' '))
            else:
                fin_arr.append(item)
        return fin_arr, line

    def process_line(self, line, add_line=True, trgs=None):
        patterns = [self.pattern_Start, self.pattern_End]
        for index, pattern in enumerate(patterns):
            block = re.search(pattern=pattern, string=re.sub(r'\s+', ' ', line), flags=re.DOTALL)
            if block:
                if index == 0 and not self.ref:
                    self.data = {}
                    header_labels = list(filter(lambda x: x != '', line.split('  ')))
                    for index, h in enumerate(header_labels):
                        key = h.strip()
                        self.data[key] = []
                        if key == self.lineitem_desc_label:
                            self.lineitem_position = index
                    self.ref = True
                    return
                elif index == 1 and add_line:
                    if re.search(r"\.00", line):
                        values = self.get_value(line, trgs)
                        if values and len(values) == len(self.data):
                            self.ref = True
                        else:
                            self.ref = False
                    return

        if self.ref and add_line:
            if re.search(r"\.00", line):
                values = self.get_value(line, trgs)
                if not self.has_matching_pattern(self.ignore_words, line):
                    if values and len(values) == len(self.data) and values[self.lineitem_position] != '':
                        for i, item in enumerate(values):
                            keys_list = list(self.data.keys())
                            self.data[keys_list[i]].append(item)

    def get_value(self, line, trgs):
        line_arr, line = self.check_line_arr(list(filter(lambda x: x != '', line.split('  '))), line)
        final_line_arr = []
        start_index, end_index = 0, 0
        for index, l in enumerate(line_arr):
            if index == 0:
                final_line_arr.append(l)
                start_index, end_index = line.index(l, end_index), len(l)
            else:
                ref_count = self.linedescriptionLmt if index == self.lineitem_position else 14
                if l in line and line.index(l, end_index) - start_index <= ref_count:
                    final_line_arr.append(l)
                    start_index, end_index = line.index(l, end_index), len(l)
                else:
                    final_line_arr.append('')
                    final_line_arr.append(l)
                    start_index, end_index = line.index(l, end_index), len(l)
        return final_line_arr

    def startPreparation(self):
        matched_heads = []
        with open(self.filename, 'r') as f:
            if re.search(self.head, f.read(), flags=re.DOTALL):
                matched_heads.append(self.head)
                for kws in self.keywords:
                    patterns = [kws['start'], kws['end']]
                    with open(self.filename, 'r') as file:
                        for line in file:
                            # print(line)
                            self.process_line(line.strip(), patterns, kws['ref'], kws)
            else:
                print('Header not found:', self.head)
        return [self.results, matched_heads]

    @staticmethod
    def preInitiate(cfg, filename):
        initiate = DataPreparationTool(cfg, filename)
        res = initiate.startPreparation()
        return res

# Load configuration and process the file
def load_config_and_process_file(config_path, file_path):
    try:
        with open(config_path, 'r') as config_file:
            cfg = json.load(config_file)
            result = DataPreparationTool.preInitiate(cfg, file_path)
            return result
    except Exception as e:
        print("An error occurred:", e)

# Example usage
if __name__ == "__main__":
    config_file_path = 'fosse.json'
    data_file_path = 'D:\\FOSSE\\7\\D A I L Y   C L O S I N G   R E P O R T   S U M M A R Y-7thjuly.txt'
    results = load_config_and_process_file(config_file_path, data_file_path)
    print(results)
