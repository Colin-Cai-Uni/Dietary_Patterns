#!/bin/bash
python3 ../../cluster_analysis.py ADC/day_aggregation.csv ADC/Key/input_columns.txt kmeans 2 -pca 5 -loadings ADC/Key/pca_loadings.csv -export cluster ADC/Key/pca_clusters.csv