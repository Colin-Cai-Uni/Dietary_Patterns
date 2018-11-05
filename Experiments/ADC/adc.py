import pandas as pd
import numpy as np
import argparse
import os

INTAKES = ['drinks', 
           'Energy, with dietary fibre (kJ)', 
           'Protein (g)', 
           'Total fat (g)', 
           'Carbohydrates', 
           'Total sugars (g)', 
           'Added sugars (g)', 
           'Dietary fibre (g)', 
           'Vitamin A retinol equivalents (µg)', 
           'Thiamin (B1) (mg)', 
           'Riboflavin (B2) (mg)', 
           'Niacin (B3) (mg)', 
           'Total Folates  (µg)', 
           'Vitamin B6 (mg)', 
           'Vitamin B12  (µg)', 
           'Vitamin C (mg)', 
           'Vitamin E (mg)', 
           'Calcium (Ca) (mg)', 
           'Iodine (I) (µg)', 
           'Iron (Fe) (mg)', 
           'Magnesium (Mg) (mg)', 
           'Phosphorus (P) (mg)', 
           'Potassium (K) (mg)', 
           'Selenium (Se) (µg)', 
           'Sodium (Na) (mg)', 
           'Zinc (Zn) (mg)', 
           'Saturated fat (g)', 
           'Monounsaturated fat (g)', 
           'Polyunsaturated fat (g)']

def main():
    directory = os.path.dirname(__file__)

    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help = 'Input file')
    parser.add_argument('outfile', help = 'Output file')

    args = parser.parse_args()

    df = pd.read_csv(os.path.join(directory, args.infile))

    for i in INTAKES:
        df[i] = df[i]/df['total']

    df.to_csv(os.path.join(directory, args.outfile), index = False)

if __name__ == "__main__":
    main()