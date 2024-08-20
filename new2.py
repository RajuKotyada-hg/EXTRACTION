from new1 import TextBin
import argparse
from tabulate import tabulate
import os

if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("D:\\FOSSE\\7\\D A I L Y   C L O S I N G   R E P O R T   S U M M A R Y-7thjuly.txt", type=str, help="text file to analyze")
    parser.add_argument("--output", type=str, help="output dir to write tables to")
    parser.add_argument("--view", action='store_true', help="print extracted tables")
    args = parser.parse_args()

    tb = TextBin(args.txt_file)
    tb.make_tables()
    tables = tb.get_tables()

    for t, table in enumerate(tables):
        if args.view:
            print(tabulate(table, headers='keys', tablefmt='psql'))
        if args.output:
            table.to_csv(os.path.join(args.output, 'output_{:03d}.csv'.format(t)))