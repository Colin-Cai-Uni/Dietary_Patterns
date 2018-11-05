#!/bin/bash
Rscript ../../cluster_analysis.r ../../../Data/day_aggregation.csv input_columns.txt 5 -export labels.csv
python3 ../../label.py ../Data/day_aggregation.csv Raw/Questionnaire/labels.csv cluster Raw/Questionnaire/raw_clusters.csv cluster