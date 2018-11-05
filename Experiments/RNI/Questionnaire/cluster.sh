#!/bin/bash
Rscript ../../cluster_analysis.R ../day_aggregation.csv input_columns.txt 5 -export labels.csv
python3 ../../label.py RNI/day_aggregation.csv RNI/Questionnaire/labels.csv cluster RNI/Questionnaire/raw_clusters.csv cluster