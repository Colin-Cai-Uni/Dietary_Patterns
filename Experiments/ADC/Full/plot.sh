#!/bin/bash
python3 ../../plot.py ADC/Full/raw_clusters.csv -bar_columns ADC/Full/bar_columns.txt -box_columns ADC/Full/box_columns.txt -cluster_column cluster ADC/Full/raw_plots
python3 ../../plot.py ADC/Full/pca_clusters.csv -box_columns ADC/Full/pca_components.txt -cluster_column cluster ADC/Full/pca_plots