#!/bin/bash
python3 ../../cluster_analysis.py EC/day_aggregation.csv EC/Key/input_columns.txt -scaler robust kmeans 2 -pca 3 -loadings EC/Key/pca_loadings.csv -export cluster EC/Key/pca_clusters.csv