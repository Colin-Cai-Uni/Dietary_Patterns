#!/bin/bash
Rscript ../../cluster_analysis.R ../day_aggregation.csv input_columns.txt 5 -export labels.csv
python3 ../../label.py ADC/day_aggregation.csv ADC/Questionnaire/labels.csv cluster ADC/Questionnaire/raw_clusters.csv cluster