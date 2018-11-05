import pandas as pd
import numpy as np
import argparse
import os

def main():
    directory = os.path.dirname(__file__)

    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help = 'Input file')
    parser.add_argument('outfile', help = 'Output file')

    args = parser.parse_args()

    df = pd.read_csv(os.path.join(directory, args.infile))

    nonlipids = {'Protein (g)': 'Energy Contribution of Proteins',
                 'Carbohydrates': 'Energy Contribution of Carbohydrates',
                 'Total sugars (g)': 'Energy Contribution of Sugars',
                 'Added sugars (g)': 'Energy Contribution of Added Sugars',
                 'Dietary fibre (g)': 'Energy Contribution of Dietary Fibres'}

    lipids = {'Total fat (g)': 'Energy Contribution of Fats',
              'Saturated fat (g)': 'Energy Contribution of Saturated Fats',
              'Monounsaturated fat (g)': 'Energy Contribution of Monounsaturated Fats',
              'Polyunsaturated fat (g)': 'Energy Contribution of Polyunsaturated Fats'}

    for c in nonlipids:
        df[nonlipids[c]] = 16.7*df[c]/df['Energy, with dietary fibre (kJ)']

    for c in lipids:
        df[lipids[c]] = 37.7*df[c]/df['Energy, with dietary fibre (kJ)']

    df[df['Energy, with dietary fibre (kJ)'] > 0].to_csv(os.path.join(directory, args.outfile), index = False)

if __name__ == "__main__":
    main()