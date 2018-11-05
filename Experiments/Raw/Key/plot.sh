#!/bin/bash
python3 ../../plot.py Raw/Key/raw_clusters.csv -bar_columns Raw/Key/bar_columns.txt -box_columns Raw/Key/box_columns.txt -cluster_column cluster Raw/Key/raw_plots
python3 ../../plot.py Raw/Key/pca_clusters.csv -box_columns Raw/Key/pca_components.txt -cluster_column cluster Raw/Key/pca_plots