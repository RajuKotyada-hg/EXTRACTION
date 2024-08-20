import pandas as pd
# Example DataFrame
data = {
    'Column1': ['  Apple ', ' Banana ', '  Orange'],
    'Column2': ['  Red', ' Blue  ', 'Green  '],
    'Column3': ['   Cat  ', '   Dog', 'Bird   ']
}

df = pd.DataFrame(data)
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

print(df)