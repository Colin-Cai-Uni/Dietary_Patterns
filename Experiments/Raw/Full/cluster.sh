#!/bin/bash
python3 ../../cluster_analysis.py ../Data/day_aggregation.csv Raw/Full/input_columns.txt kmeans 2 -pca 16 -loadings Raw/Full/pca_loadings.csv -export cluster Raw/Full/pca_clusters.csv