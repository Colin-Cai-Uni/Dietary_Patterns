import pandas as pd
import numpy as np
import os

directory = os.path.dirname(__file__)

file = os.path.join(directory, os.pardir, 'Data/day_aggregation.csv')

day_columns = ['email',
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

days = pd.read_csv(file, usecols = day_columns)

days = days.groupby(day_columns).size().reset_index(name = 'counts')
days = days.groupby(['email', 'date']).size().reset_index(name = 'counts')
days = days.groupby(['email'], as_index = False).agg({'date': 'count', 'counts': 'max'})

days = days[days['counts'] == 1]
days = days[days['date'] >= 2]
days = days[['email']]

result = pd.read_csv(file)

result = result.merge(days, left_on = 'email', right_on = 'email', how = 'inner')

result.to_csv('../Data/day_aggregation.csv', index = False)