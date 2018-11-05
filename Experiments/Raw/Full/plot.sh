#!/bin/bash
python3 ../../plot.py Raw/Full/raw_clusters.csv -bar_columns Raw/Full/bar_columns.txt -box_columns Raw/Full/box_columns.txt -cluster_column cluster Raw/Full/raw_plots
python3 ../../plot.py Raw/Full/pca_clusters.csv -box_columns Raw/Full/pca_components.txt -cluster_column cluster Raw/Full/pca_plots