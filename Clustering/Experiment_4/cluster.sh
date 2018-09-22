#!/bin/bash
python3 ../cluster_analysis.py Experiment_4/data.csv Experiment_4/input_columns.txt kmeans 2 -pca 5 -export Experiment_4/clusters.csv
