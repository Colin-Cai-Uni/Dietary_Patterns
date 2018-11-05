import pandas as pd
import numpy as np
import os
import copy

# One of the column deletion operation triggers a false positive for SettingWithCopyWarning
pd.options.mode.chained_assignment = None

RECOMMENDATIONS = {'fruit_serves': {1: 2, 2: 2},
                   'veg_serves': {1: 6, 2: 5},
                   'cereal_serves': {1: 6, 2: 6},
                   'dairy_serves': {1: 2.5, 2: 2.5}}

with open('questionnaire_columns.txt') as f:
    QUESTIONNAIRE_COLUMNS = f.read().splitlines()

with open('survey_columns.txt') as f:
    SURVEY_COLUMNS = f.read().splitlines()

with open('grouping_columns.txt') as f:
    GROUPING_COLUMNS = f.read().splitlines()

with open('liquid_columns.txt') as f:
    LIQUID_COLUMNS = f.read().splitlines()

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
                       'Polyunsaturated fat (g)': 'sum'}

MANUAL_DISCARDS = ["Nachos Vegetables with Guac, Guzman Y Gomez ",
                   "Moroccan lamb, Sumo Salad"]

def main():
    directory = os.path.dirname(__file__)

    # Processing the survey dataset
    surveys_file = os.path.join(directory, os.pardir, 'Data/surveys.csv')
    surveys = pd.read_csv(surveys_file, usecols = SURVEY_COLUMNS)
    surveys['email'] = surveys['email'].str.lower()
    surveys = discard_unknown_gender(surveys)
    surveys = discard_erroneous_measurements(surveys)
    surveys = discard_survey_clashes(surveys)

    for c in SURVEY_COLUMNS:
        surveys[c].fillna(-1, inplace = True)

    for c in RECOMMENDATIONS:
        surveys[c] = surveys.apply(apply_serving_guidelines, serving = c, axis = 1)

    surveys['bmi'] = surveys['weight']/np.square(surveys['height']/100.0)
    SURVEY_COLUMNS.append('bmi')

    # Processing the questionnaires dataset
    questionnaires_file = os.path.join(directory, os.pardir, 'Data/questionnaires_reduced.csv')
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
    meals['date'] = meals['date'].apply(lambda time: time.split(' ')[0])
    meals = mark_for_discard(meals)
    meals = discard_duplicate_items(meals)
    
    liquids_file = os.path.join(directory, os.pardir, 'Data/liquids.csv')
    liquids = pd.read_csv(liquids_file, usecols = LIQUID_COLUMNS)
    meals = meals.merge(liquids, left_on = 'foodName', right_on = 'foodName', how = 'inner')
    meals['drinks'] = np.where(meals['is liquid'], meals['total'], 0)

    # Combining the datasets
    combination = surveys.merge(questionnaires, left_on = 'email', right_on = 'username', how = 'inner')
    combination = combination.merge(meals, left_on = ['email', 'date'], right_on = ['username', 'date'], how = 'inner')

    for c in AGGREGATION_COLUMNS:
        combination[c].fillna(0, inplace = True)
    
    # Day-level combination
    day_agg = day_aggregation(combination)
    day_agg['bmr'] = day_agg.apply(bmr, axis = 1)
    day_agg['bmr multiplier'] = day_agg['Energy, with dietary fibre (kJ)']/day_agg['bmr']
    day_agg = apply_lower_multiplier_threshold(day_agg)
    day_agg = apply_upper_multiplier_threshold(day_agg)
    day_agg = discard_marked(day_agg)
    day_agg = discard_insufficient_entries(day_agg)

    # Meal-level aggregation
    meal_agg = meal_aggregation(combination, day_agg[['email', 'date']], 'Full')
    meal_agg_solid = meal_aggregation(combination[~combination['is liquid']], day_agg[['email', 'date']], 'Solid')
    meal_agg_liquid = meal_aggregation(combination[combination['is liquid'] & ~combination['is water']], day_agg[['email', 'date']], 'Liquid')

    # Subject-level aggregation
    subject_agg = subject_aggregation(day_agg)

    day_agg_file = os.path.join(directory, os.pardir, 'Data/day_aggregation.csv')
    day_agg.to_csv(day_agg_file, index = False)

    meal_agg_file = os.path.join(directory, os.pardir, 'Data/meal_aggregation.csv')
    meal_agg.to_csv(meal_agg_file, index = False)

    meal_agg_solid_file = os.path.join(directory, os.pardir, 'Data/meal_aggregation_solid.csv')
    meal_agg_solid.to_csv(meal_agg_solid_file, index = False)

    meal_agg_liquid_file = os.path.join(directory, os.pardir, 'Data/meal_aggregation_liquid.csv')
    meal_agg_liquid.to_csv(meal_agg_liquid_file, index = False)

    subject_agg_file = os.path.join(directory, os.pardir, 'Data/subject_aggregation.csv')
    subject_agg.to_csv(subject_agg_file, index = False)

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

def discard_erroneous_measurements(surveys):
    initial_subjects = len(surveys.index)

    surveys = surveys[(surveys['height'] > 0) & (surveys['weight'] > 0)]

    remaining_subjects = len(surveys.index)

    print('Discarding Subjects with Erroneous Measurements:\nSurvey Subjects: %d -> %d\n' % 
        (initial_subjects, remaining_subjects))

    return surveys

def apply_serving_guidelines(row, serving):
    return row[serving] - RECOMMENDATIONS[serving][row['gender']]

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

    discards = len(meals[meals['manual discard']].index)

    print('Marking Meal Items to Discard:\n%d Marked\n' % 
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
    groupings = copy.deepcopy(GROUPING_COLUMNS)
    groupings[0] = 'email'

    results = copy.deepcopy(AGGREGATION_COLUMNS)
    results['foodtype'] = pd.Series.nunique
    results['manual discard'] = 'max'

    day_agg = combination.groupby(groupings, as_index = False).agg(results)

    daily_entries = len(day_agg.index)

    print('Performing Day-Level Combination:\nDaily Entries: %d\n' % 
        (daily_entries))

    return day_agg

def bmr(row):
    if row['gender'] == 1:
        return 64*row['weight'] + 2840
    else:
        return 61.5*row['weight'] + 2080

def meal_aggregation(combination, day_agg, subtype):
    groupings = copy.deepcopy(GROUPING_COLUMNS)
    groupings[0] = 'email'
    groupings.append('foodtype')

    results = copy.deepcopy(AGGREGATION_COLUMNS)
    results['foodName'] = ';'.join

    meal_agg = combination.groupby(groupings, as_index = False).agg(results)
    day_agg = day_agg[['email', 'date']]
    meal_agg = meal_agg.merge(day_agg, left_on = ['email', 'date'], right_on = ['email', 'date'], how = 'inner')

    meal_entries = len(meal_agg.index)

    print('Performing Meal-Level Combination (%s):\nMeal Entries: %d\n' % 
        (subtype, meal_entries))

    return meal_agg

def subject_aggregation(day_agg):
    groupings = copy.deepcopy(SURVEY_COLUMNS)

    results = copy.deepcopy(AGGREGATION_COLUMNS)
    results['date'] = pd.Series.nunique

    subject_agg = day_agg.groupby(groupings, as_index = False).agg(results)

    subject_entries = len(subject_agg.index)

    print('Performing Subject-Level Combination:\nSubject Entries: %d\n' % 
        (subject_entries))

    return subject_agg

def discard_marked(df):
    initial_entries = len(df.index)

    df = df[df['manual discard'] == False]
    df.drop(columns=['manual discard'], inplace = True)

    remaining_entries = len(df.index)

    print('Discarding Marked Entries:\nDaily Entries: %d -> %d\n' % 
        (initial_entries, remaining_entries))

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