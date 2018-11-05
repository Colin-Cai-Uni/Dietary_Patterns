#!/bin/bash
python3 ../../plot.py ADC/Key/raw_clusters.csv -bar_columns ADC/Key/bar_columns.txt -box_columns ADC/Key/box_columns.txt -cluster_column cluster ADC/Key/raw_plots
python3 ../../plot.py ADC/Key/pca_clusters.csv -box_columns ADC/Key/pca_components.txt -cluster_column cluster ADC/Key/pca_plots