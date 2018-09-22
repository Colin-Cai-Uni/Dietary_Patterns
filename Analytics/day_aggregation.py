import pandas as pd
import numpy as np
import os

directory = os.path.dirname(__file__)

surveys_file = os.path.join(directory, os.pardir, 'Data/surveys.csv')
questionnaires_file = os.path.join(directory, os.pardir, 'Data/questionnaires.csv')
meals_file = os.path.join(directory, os.pardir, 'Data/meals.xlsx')

survey_columns = ['email',
                  'gender',
                  'weight']
surveys = pd.read_csv(surveys_file, usecols = survey_columns)
surveys['email'] = surveys['email'].str.lower()

questionnaire_columns = ['username',
                         'date',
                         'q1_value',
                         'q2_value',
                         'q3_check_1',
                         'q3_check_2',
                         'q3_check_3',
                         'q3_check_4',
                         'q3_check_5',
                         'q3_check_6',
                         'q3_check_6_answer',
                         'q4_value',
                         'q5_value',
                         'q6_value',
                         'q7_value']

questionnaires = pd.read_csv(questionnaires_file, usecols = questionnaire_columns)
questionnaires = questionnaires.drop_duplicates()

questionnaires['username'] = questionnaires['username'].str.lower()
questionnaires['q3_check_6_answer'].fillna('', inplace = True)
questionnaires['q3_check_6_answer'] = questionnaires['q3_check_6_answer'].apply(lambda x: x != '')

meal_types = {'date': str}
meals = pd.read_excel(meals_file, dtype = meal_types)
meals['username'] = meals['username'].str.lower()
meals['drinks'] = np.where(meals['serving unit'].str[-1] == 'L', meals['total'], 0)

meals = meals[~((meals[['date', 'username', 'foodtype', 'location', 'foodName', 'amount']].duplicated(keep = 'first')) & (meals['foodtype'] != 'Snacks & Drinks'))]

aggregation = surveys.merge(questionnaires, left_on = 'email', right_on = 'username', how = 'inner')
aggregation = aggregation.merge(meals, left_on = 'email', right_on = 'username', how = 'inner')

aggregation['date_y'] = aggregation['date_y'].apply(lambda time: time.split(' ')[0])
aggregation = aggregation[aggregation['date_x'] == aggregation['date_y']]

aggregation.rename(columns = {'date_x': 'date'}, inplace = True)

groupings = ['email',
            'date',
            'q1_value',
            'q2_value',
            'q3_check_1',
            'q3_check_2',
            'q3_check_3',
            'q3_check_4',
            'q3_check_5',
            'q3_check_6',
            'q3_check_6_answer',
            'q4_value',
            'q5_value',
            'q6_value',
            'q7_value',
            'gender',
            'weight']

results = {'foodtype': pd.Series.nunique,
           'total': 'sum',
           'drinks': 'sum',
           'Energy, with dietary fibre (kJ)': 'sum',
           'Protein (g)': 'sum',
           'Total fat (g)': 'sum',
           'Carbohydrates': 'sum',
           'Total sugars (g)': 'sum',
           'Added sugars (g)': 'sum',
           'Dietary fibre (g)': 'sum',
           'Vitamin A retinol equivalents (µg)': 'sum',
           'Thiamin (B1) (mg)': 'sum',
           'Riboflavin (B2) (mg)': 'sum',
           'Niacin (B3) (mg)': 'sum',
           'Total Folates  (µg)': 'sum',
           'Vitamin B6 (mg)': 'sum',
           'Vitamin B12  (µg)': 'sum',
           'Vitamin C (mg)': 'sum',
           'Vitamin E (mg)': 'sum',
           'Calcium (Ca) (mg)': 'sum',
           'Iodine (I) (µg)': 'sum',
           'Iron (Fe) (mg)': 'sum',
           'Magnesium (Mg) (mg)': 'sum',
           'Phosphorus (P) (mg)': 'sum',
           'Potassium (K) (mg)': 'sum',
           'Selenium (Se) (µg)': 'sum',
           'Sodium (Na) (mg)': 'sum',
           'Zinc (Zn) (mg)': 'sum',
           'Saturated fat (g)': 'sum',
           'Monounsaturated fat (g)': 'sum',
           'Polyunsaturated fat (g)': 'sum'}

for r in results:
    aggregation[r].fillna(0, inplace = True)

aggregation = aggregation.groupby(groupings, as_index = False).agg(results)

def bmr(row, gender, weight):
    if row[gender] == 1:
        return 64*row[weight] + 2840
    else:
        return 61.5*row[weight] + 2080

aggregation['bmr'] = aggregation.apply(bmr, gender = 'gender', weight = 'weight', axis = 1)
aggregation['bmr multiplier'] = aggregation['Energy, with dietary fibre (kJ)']/aggregation['bmr']

aggregation = aggregation[aggregation['bmr multiplier'] > 0.5]
aggregation = aggregation[aggregation['bmr multiplier'] < 3.0]

aggregation.to_csv('../Data/day_aggregation.csv', index = False)