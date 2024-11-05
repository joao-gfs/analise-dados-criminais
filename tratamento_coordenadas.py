import pandas as pd

df = pd.read_csv('dataset_original.csv', sep=';')

print(df.info())