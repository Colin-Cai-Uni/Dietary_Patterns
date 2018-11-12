import numpy as np
import pandas as pd
from sklearn import preprocessing
from scipy.spatial import distance
import copy
import re

# This script took the meals dataset as the input and outputs a list of unique meal items marked by
# whether they are beverages and whether they are water

df = pd.read_excel('meals.xlsx')
df = df.drop_duplicates(subset = ['foodName', 'serving unit'])
units = copy.deepcopy(df)

whitelist = set(['smoothie', 'juice', 'shake'])
blacklist = set(['oil', 'soup', 'curry', 'laksa', 'dressing', 'mayonnaise', 'sauce', 'cheese', 'mustard', 'stock', 'bread', 'vinaigrette', 'broth', 'yoghurt'])

manual_removal = ['Vinegar (except balsamic)', 'Choc Protein Ball, Boost Juice', 'Sea Salt Popcorn, Boost Juice', 'Coconut cream']

units = units.groupby('foodName', as_index = False).agg({'serving unit': ';'.join})
units = units[['foodName', 'serving unit']]

df.drop(columns = ['id','date','username','foodtype','recordingtime','location','amount','serving unit','serving size','weigh','inputtype'], inplace = True)
df = df.merge(units, left_on = 'foodName', right_on = 'foodName', how = 'inner')
df = df.drop_duplicates(subset = ['foodName'])

def check_list(col, lst):
    return bool(lst & set(re.findall(r"[\w']+", col.lower())))

def no_solid(col):
    return not any(i[-1] == 'g' for i in col.lower().split(';'))

def has_liquid(col):
    return any(i[-1] == 'L' or i[-2:] == 'ml' for i in col.split(';'))

# Items are considered liquids if they satisfy the has_liquid heuristic or contain a word in the whitelist
# AND do not contain a word in the blacklist or exist in the manual_removal list
df['blacklisted'] = df['foodName'].apply(check_list, lst = blacklist) | df['foodName'].apply(lambda x: x in manual_removal)
df['whitelisted'] = df['foodName'].apply(check_list, lst = whitelist) & df['serving unit'].apply(no_solid)
df['is liquid'] = ~df['blacklisted'] & (df['serving unit'].apply(has_liquid) | df['whitelisted'])

nutrients = ['Energy, with dietary fibre (kJ)',
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

for c in nutrients:
    df[c] = df[c].fillna(0)/df['total']

df.reset_index(inplace = True)

df['has water'] = df['foodName'].apply(lambda x: 'water' in x.lower())

index = df.index[df['foodName'] == 'Tap water'].tolist()[0]

scaler = preprocessing.MinMaxScaler()
X = scaler.fit_transform(df[nutrients])
Y = X[index].reshape(1, X.shape[1])

df['dist'] = distance.cdist(X, Y, 'euclidean')

water = ['Tap water', 'Bore water', 'Frantelle Water', 'Bottled/filtered/tank water', 'Cool Ridge Water']

df['is water'] = df['foodName'].apply(lambda x: x in water)

df.to_csv('liquids.csv', index = False)
