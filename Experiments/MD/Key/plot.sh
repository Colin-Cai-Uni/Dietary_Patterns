#!/bin/bash
python3 ../../plot.py EC/Key/raw_clusters.csv -bar_columns EC/Key/bar_columns.txt -box_columns EC/Key/box_columns.txt -cluster_column cluster EC/Key/raw_plots
python3 ../../plot.py EC/Key/pca_clusters.csv -box_columns EC/Key/pca_components.txt -cluster_column cluster EC/Key/pca_plots