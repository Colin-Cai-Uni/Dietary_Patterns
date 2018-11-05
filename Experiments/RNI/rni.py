import pandas as pd
import numpy as np
import argparse
import os

def l1_norm(row, columns):
    divisor = 0

    for c in columns:
        divisor += row[c]

    return divisor

def main():
    directory = os.path.dirname(__file__)

    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help = 'Input file')
    parser.add_argument('outfile', help = 'Output file')

    args = parser.parse_args()

    df = pd.read_csv(os.path.join(directory, args.infile))

    df['Sodium (Na) (mg)'] = df['Sodium (Na) (mg)']/1000
    df.rename(columns = {'Sodium (Na) (mg)': 'Sodium (Na) (g)'}, inplace = True)

    key_values = ['Protein (g)',
                  'Total fat (g)',
                  'Carbohydrates',
                  'Sodium (Na) (g)']

    df['l1 norm'] = df.apply(l1_norm, columns = key_values, axis = 1)

    key_values += ['Saturated fat (g)', 'Total sugars (g)', 'Dietary fibre (g)']

    for v in key_values:
        df[v] = df[v]/df['l1 norm']

    df.to_csv(os.path.join(directory, args.outfile), index = False)

if __name__ == "__main__":
    main()