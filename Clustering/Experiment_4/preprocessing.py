import pandas as pd
import numpy as np
import os

directory = os.path.dirname(__file__)

input_file = os.path.join(directory, os.pardir, os.pardir, 'Data/day_aggregation.csv')
df = pd.read_csv(input_file)

values = ['drinks',
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

for v in values:
    df[v] = df[v]/df['total']

df.to_csv('data.csv')