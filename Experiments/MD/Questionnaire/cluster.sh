#!/bin/bash
Rscript ../../cluster_analysis.R ../day_aggregation.csv input_columns.txt 5 -export labels.csv
python3 ../../label.py MD/day_aggregation.csv MD/Questionnaire/labels.csv cluster MD/Questionnaire/raw_clusters.csv cluster