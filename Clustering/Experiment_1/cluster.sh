#!/bin/bash
python3 ../cluster_analysis.py ../Data/day_aggregation.csv Experiment_1/input_columns.txt kmeans 5 -pca 18 -export Experiment_1/clusters.csv