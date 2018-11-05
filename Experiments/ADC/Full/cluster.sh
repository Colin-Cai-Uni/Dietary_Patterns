#!/bin/bash
python3 ../../cluster_analysis.py ADC/day_aggregation.csv ADC/Full/input_columns.txt kmeans 2 -pca 17 -loadings ADC/Full/pca_loadings.csv -export cluster ADC/Full/pca_clusters.csv