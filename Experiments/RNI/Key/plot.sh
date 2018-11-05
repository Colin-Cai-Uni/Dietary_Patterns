#!/bin/bash
python3 ../../plot.py RNI/Key/raw_clusters.csv -bar_columns RNI/Key/bar_columns.txt -box_columns RNI/Key/box_columns.txt -cluster_column cluster RNI/Key/raw_plots
python3 ../../plot.py RNI/Key/pca_clusters.csv -box_columns RNI/Key/pca_components.txt -cluster_column cluster RNI/Key/pca_plots