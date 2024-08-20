import mac as cam
import pandas as pd
import pandas as pd
import numpy as np
from re import sub
from decimal import Decimal
import mac as cam
from tabulate import tabulate
import json,re,os

def extract_tables(self, table_idx, tk):
    try:
        cols, rows = self._generate_columns_and_rows(table_idx, tk)
    except ValueError as e:
        print(f"Error in extracting columns and rows: {e}")
        # Handle the error or re-raise it
        raise

def _generate_columns_and_rows(self, table_idx, tk):
    t_bbox = self.t_bbox  # Assuming t_bbox is set elsewhere
    text_x_min, text_y_min, text_x_max, text_y_max = self._text_bbox(t_bbox)
    # Continue with the rest of your logic

def _text_bbox(self, t_bbox):
    if not t_bbox or not any(t_bbox.values()):
        raise ValueError("t_bbox is empty or not structured properly")
    
    print("t_bbox contents:", t_bbox)  # Add logging to inspect t_bbox
    
    xmin = min([t.x0 for direction in t_bbox for t in t_bbox[direction]])
    text_y_min = min([t.y0 for direction in t_bbox for t in t_bbox[direction]])
    text_x_max = max([t.x1 for direction in t_bbox for t in t_bbox[direction]])
    text_y_max = max([t.y1 for direction in t_bbox for t in t_bbox[direction]])
    return xmin, text_y_min, text_x_max, text_y_max
input_pdf = 'C:\\Users\\raju.kotyada\\Downloads\\Finance Management Report 6.11.24.pdf'
# tables = cam.read_pdf(input_pdf, flag_size=True)
tables = cam.read_pdf(input_pdf, pages="all", flavor='stream', flag_size=True)

for table in tables:
    df: pd.DataFrame = table.df
