import array
import copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class TextBin:

    def __init__(self, filename):
        self.fname = filename
        self.params = {
            'sim_thres': 0.15, 'diff_thres': 0.3, 'sq_thres': 0.5
        }
        self.tables = []
        self.dist_mat = None

    def get_params(self):
        return copy.deepcopy(self.params)

    def set_params(self, k, v):
        assert k in self.params, "bad dog!"
        self.params[k] = v

    def make_tables(self):
        self.tables = []
        text, b = self._read_file()
        s = self._parwise_sim(b, **self.params)
        self._make_tables(s, text, b)

    def get_tables(self):
        return self.tables

    def _make_tables(self, s, text, b):

        table_lines = []
        table_cols = []
        for i, x in enumerate(s):
            if x == 0:
                continue
            table_lines.append(text[i + 1 - x:i + 1])
            bin = (np.sum(~b[i + 1 - x:i + 1], axis=0) > 0).astype(int)
            table_cols.append(self._find_blobs(bin))

        for lines, cols in zip(table_lines, table_cols):
            num_cols = len(cols)//2
            col_vals = {i:[] for i in range(num_cols)}
            for line in lines:
                if len(line) < cols[-1]+1:
                    line += " "*(cols[-1]+1-len(line))
                for i in range(num_cols):
                    s,e = cols[2*i:2*(i+1)]
                    col_vals[i].append(line[s:e+1])
            self.tables.append(pd.DataFrame(col_vals))

    def _find_blobs(self, b):
        cols = []
        reset = True
        for i, x in enumerate(b):
            if not x:
                if not reset:
                    cols.append(i - 1)
                    reset = True
                continue
            if reset:
                cols.append(i)
                reset = False
            else:
                continue
        if not reset:
            cols.append(len(b))

        assert not len(cols) % 2, "blobs are not even!"
        return cols

    def _read_file(self):

        with open(self.fname) as fp:
            lines = []
            l = fp.readline()
            max_len = 0
            while len(l) > 0:
                lines.append(l.rstrip('\n'))
                max_len = max(max_len, len(l))
                l = fp.readline()

            b = np.ones(shape=(len(lines), max_len), dtype=bool)
            for il, l in enumerate(lines):
                b[il, :len(l)] = np.array([c==' ' for c in l])

            return lines, b

    def _parwise_sim(self, b, sim_thres=0.1, diff_thres=0.2, sq_thres=0.7):

        bla = np.logical_xor(np.expand_dims(b,0), np.expand_dims(b,1))
        pw_dist = np.mean(bla.astype(float), axis=2)

        pw_dist = (pw_dist < sim_thres) - 1*(pw_dist > diff_thres)
        self.dist_mat = pw_dist

        l = pw_dist.shape[0]
        pw_dist_cnt = np.zeros(shape=(l,l,))

        pw_dist_cnt[0,:] = 1.
        for k in range(1,l):
            for i in range(0,l):
                if k>i:
                    continue
                if pw_dist_cnt[k-1, i-1] < 0. or np.any(pw_dist[i-k:i, i] < 0.):
                    pw_dist_cnt[k,i] = -1 # reject if square contains ANY bad eggs
                    continue
                pw_dist_cnt[k,i] = pw_dist_cnt[k-1,i-1] + np.sum(pw_dist[i-k:i, i])*2 + 1.

        len_a = np.expand_dims(np.arange(1,l+1), axis=(1,))
        sq_a = np.power(len_a, 2)
        pw_dist_cnt = pw_dist_cnt / sq_a
        s = np.max((pw_dist_cnt > sq_thres).astype(int)*len_a, axis=0)
        s[s < 2] = 0.

        for i,x in enumerate(s[::-1]):
            j = len(s)-i
            t = s[j-x:j-1] - x
            s[j-x:j-1][t<0] = 0

        return s

if __name__=="__main__":

    tb = TextBin('table.txt')
    tb.make_tables()

    for t in tb.tables:
        print(t)

    plt.imshow(tb.dist_mat)
    plt.xlabel('line')
    plt.ylabel('line')
    plt.title('Similarity matrix')
    plt.show()