#!/bin/bash
python3 ../cluster_analysis.py ../Data/day_aggregation.csv Experiment_2/input_columns.txt kmeans 5 -pca 10 -export Experiment_2/clusters.csv
