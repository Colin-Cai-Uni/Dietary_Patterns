#!/bin/bash
python3 ../../cluster_analysis.py ../Data/day_aggregation.csv Raw/Key/input_columns.txt kmeans 2 -pca 5 -loadings Raw/Key/pca_loadings.csv -export cluster Raw/Key/pca_clusters.csv