#!/bin/bash
python3 ../cluster_analysis.py ../Data/day_aggregation_final.csv Experiment_3/input_columns.txt kmeans 2 -pca 5 -export Experiment_3/clusters.csv
