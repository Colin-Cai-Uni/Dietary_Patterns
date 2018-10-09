import pandas as pd
import numpy as np
import os
import copy

# One of the column deletion operation triggers a false positive for SettingWithCopyWarning
pd.options.mode.chained_assignment = None

SURVEY_COLUMNS = ['email',
                  'gender',
                  'weight']

QUESTIONNAIRE_COLUMNS = ['username',
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

AGGREGATION_COLUMNS = {'total': 'sum',
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
                       'Polyunsaturated fat (g)': 'sum',
                       'manual discard': 'max'}

MANUAL_DISCARDS = ["Nachos Vegetables with Guac, Guzman Y Gomez ",
                   "Moroccan lamb, Sumo Salad"]

def main():
    directory = os.path.dirname(__file__)

    # Processing the survey dataset
    surveys_file = os.path.join(directory, os.pardir, 'Data/surveys.csv')
    surveys = pd.read_csv(surveys_file, usecols = SURVEY_COLUMNS)
    surveys['email'] = surveys['email'].str.lower()
    surveys = discard_unknown_gender(surveys)
    surveys = discard_survey_clashes(surveys)

    # Processing the questionnaires dataset
    questionnaires_file = os.path.join(directory, os.pardir, 'Data/questionnaires.csv')
    questionnaires = pd.read_csv(questionnaires_file, usecols = QUESTIONNAIRE_COLUMNS)
    questionnaires = questionnaires.drop_duplicates()
    questionnaires['username'] = questionnaires['username'].str.lower()
    questionnaires['q3_check_6_answer'].fillna('', inplace = True)
    questionnaires['q3_check_6_answer'] = questionnaires['q3_check_6_answer'].apply(lambda x: x != '')
    questionnaires = discard_questionnaire_clashes(questionnaires)

    # Preprocessing the meals dataset
    meals_file = os.path.join(directory, os.pardir, 'Data/meals.xlsx')
    meals = pd.read_excel(meals_file, dtype = {'date': str})
    meals['username'] = meals['username'].str.lower()
    meals['drinks'] = np.where(meals['serving unit'].str[-1] == 'L', meals['total'], 0)
    meals = mark_for_discard(meals)
    meals = discard_duplicate_items(meals)
    
    # Combining the datasets
    combination = surveys.merge(questionnaires, left_on = 'email', right_on = 'username', how = 'inner')
    combination = combination.merge(meals, left_on = 'email', right_on = 'username', how = 'inner')
    combination['date_y'] = combination['date_y'].apply(lambda time: time.split(' ')[0])
    combination = combination[combination['date_x'] == combination['date_y']]
    combination.rename(columns = {'date_x': 'date'}, inplace = True)

    for r in AGGREGATION_COLUMNS:
        combination[r].fillna(0, inplace = True)
    
    # Day-level combination
    day_agg = day_aggregation(combination)
    day_agg['bmr'] = day_agg.apply(bmr, gender = 'gender', weight = 'weight', axis = 1)
    day_agg['bmr multiplier'] = day_agg['Energy, with dietary fibre (kJ)']/day_agg['bmr']
    day_agg = apply_lower_multiplier_threshold(day_agg)
    day_agg = apply_upper_multiplier_threshold(day_agg)
    day_agg = discard_insufficient_entries(day_agg)

    # Meal-level aggregation
    meal_agg = meal_aggregation(combination, day_agg[['email', 'date']])

    day_agg = discard_marked(day_agg, 'Day-Level Combination')
    meal_agg = discard_marked(meal_agg, 'Meal-Level Combination')

    day_agg_file = os.path.join(directory, os.pardir, 'Data/day_aggregation.csv')
    day_agg.to_csv(day_agg_file, index = False)

    meal_agg_file = os.path.join(directory, os.pardir, 'Data/meal_aggregation.csv')
    meal_agg.to_csv(meal_agg_file, index = False)

def discard_unknown_gender(surveys):
    initial_subjects = len(surveys.index)

    surveys = surveys[surveys['gender'] != 3]

    remaining_subjects = len(surveys.index)

    print('Discarding Subjects with Unknown Genders:\nSurvey Subjects: %d -> %d\n' % 
        (initial_subjects, remaining_subjects))

    return surveys

def discard_survey_clashes(surveys):
    initial_subjects = len(surveys.index)

    surveys = surveys.drop_duplicates(subset = ['email'], keep = False)

    remaining_subjects = len(surveys.index)

    print('Discarding Subjects with Survey Clashes:\nSurvey Subjects: %d -> %d\n' % 
        (initial_subjects, remaining_subjects))

    return surveys

def discard_questionnaire_clashes(questionnaires):
    initial_entries = len(questionnaires.index)

    clash_check = copy.deepcopy(questionnaires)
    clash_check = clash_check.groupby(QUESTIONNAIRE_COLUMNS).size().reset_index(name = 'counts')
    clash_check = clash_check.groupby(['username', 'date']).size().reset_index(name = 'counts')
    clash_check = clash_check.groupby(['username'], as_index = False).agg({'date': 'count', 'counts': 'max'})

    initial_subjects = len(clash_check.index)

    clash_check = clash_check[clash_check['counts'] == 1]
    clash_check = clash_check[['username']]

    remaining_subjects = len(clash_check.index)

    questionnaires = questionnaires.merge(clash_check, left_on = 'username', right_on = 'username', how = 'inner')

    remaining_entries = len(questionnaires.index)

    print('Discarding Subjects with Questionaire Clashes:\nQuestionnaire Subjects: %d -> %d\nQuestionnaire Entries: %d -> %d\n' % 
        (initial_subjects, remaining_subjects, initial_entries, remaining_entries))

    return questionnaires

def mark_for_discard(meals):
    meals['manual discard'] = meals['foodName'].apply(lambda x: x in MANUAL_DISCARDS)

    discards = len(meals.index) - len(meals[meals['manual discard']].index)

    print('Marking Meal Items to Discard:\n%d Marked' % 
        (discards))

    return meals

def discard_duplicate_items(meals):
    initial_items = len(meals.index)

    meals = meals[~((meals[['date', 'username', 'foodtype', 'location', 'foodName', 'amount']].duplicated(keep = 'first')) & (meals['foodtype'] != 'Snacks & Drinks'))]

    remaining_items = len(meals.index)

    print('Discarding Duplicate Meal Items:\nMeal Items: %d -> %d\n' % 
        (initial_items, remaining_items))

    return meals

def day_aggregation(combination):
    groupings = copy.deepcopy(QUESTIONNAIRE_COLUMNS)
    groupings[0] = 'email'
    groupings.append('gender')
    groupings.append('weight')

    results = copy.deepcopy(AGGREGATION_COLUMNS)
    results['foodtype'] = pd.Series.nunique

    day_agg = combination.groupby(groupings, as_index = False).agg(results)

    daily_entries = len(day_agg.index)

    print('Performing Day-Level Combination:\nDaily Entries: %d\n' % 
        (daily_entries))

    return day_agg

def bmr(row, gender, weight):
    if row[gender] == 1:
        return 64*row[weight] + 2840
    else:
        return 61.5*row[weight] + 2080

def meal_aggregation(combination, day_agg):
    groupings = copy.deepcopy(QUESTIONNAIRE_COLUMNS)
    groupings[0] = 'email'
    groupings.append('foodtype')

    results = copy.deepcopy(AGGREGATION_COLUMNS)
    results['foodName'] = ';'.join

    meal_agg = combination.groupby(groupings, as_index = False).agg(results)
    day_agg = day_agg[['email', 'date']]
    meal_agg = meal_agg.merge(day_agg, left_on = 'email', right_on = 'email', how = 'inner')
    meal_agg = meal_agg[meal_agg['date_x'] == meal_agg['date_y']]
    meal_agg.rename(columns = {'date_x': 'date'}, inplace = True)
    meal_agg.drop(columns=['date_y'], inplace = True)

    meal_entries = len(meal_agg.index)

    print('Performing Meal-Level Combination:\nMeal Entries: %d\n' % 
        (meal_entries))

    return meal_agg

def discard_marked(df, df_name):
    initial_entries = len(df.index)

    df = df[df['manual discard'] == False]
    df.drop(columns=['manual discard'], inplace = True)

    remaining_entries = len(df.index)

    print('Discarding Marked Entries from %s:\nEntries: %d -> %d\n' % 
        (df_name, initial_entries, remaining_entries))

    return df

def apply_lower_multiplier_threshold(day_agg):
    initial_entries = len(day_agg.index)

    day_agg = day_agg[day_agg['bmr multiplier'] > 0.5]

    remaining_entries = len(day_agg.index)

    print('Discarding Entries Below Lower BMR Multiplier Threshold:\nDaily Entries: %d -> %d\n' % 
        (initial_entries, remaining_entries))

    return day_agg

def apply_upper_multiplier_threshold(day_agg):
    initial_entries = len(day_agg.index)

    day_agg = day_agg[day_agg['bmr multiplier'] < 3.0]

    remaining_entries = len(day_agg.index)

    print('Discarding Entries Above Upper BMR Multiplier Threshold:\nDaily Entries: %d -> %d\n' % 
        (initial_entries, remaining_entries))

    return day_agg

def discard_insufficient_entries(day_agg):
    initial_entries = len(day_agg.index)

    days = day_agg.groupby(['email'], as_index = False).agg({'date': 'count'})

    initial_subjects = len(days.index)

    days = days[days['date'] >= 2]
    days = days[['email']]

    remaining_subjects = len(days.index)

    day_agg = day_agg.merge(days, left_on = 'email', right_on = 'email', how = 'inner')

    remaining_entries = len(day_agg.index)

    print('Discarding Subjects with Insufficient Daily Entries:\nSubjects: %d -> %d\nDaily Entries: %d -> %d\n' % 
        (initial_subjects, remaining_subjects, initial_entries, remaining_entries))

    return day_agg

if __name__ == "__main__":
    main()