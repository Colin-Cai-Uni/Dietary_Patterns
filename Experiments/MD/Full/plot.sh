#!/bin/bash
python3 ../../plot.py MD/Full/raw_clusters.csv -bar_columns MD/Full/bar_columns.txt -box_columns MD/Full/box_columns.txt -cluster_column cluster MD/Full/raw_plots
python3 ../../plot.py MD/Full/pca_clusters.csv -box_columns MD/Full/pca_components.txt -cluster_column cluster MD/Full/pca_plots