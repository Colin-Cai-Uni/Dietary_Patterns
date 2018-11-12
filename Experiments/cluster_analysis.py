import pandas as pd
import numpy as np
from clusterkit import ClusterKit
from sklearn import preprocessing
import argparse
import os

'''
The script used to conduct all the k-means++ clustering experiments.

General Parameters
------------------
inputfile : file location
    Location of the clustering input data. The input file should be 
    in csv format.
columns : file location
    Location of a file listing the columns to use as input features, 
    with each column on a new line.
scaler : string
    Choice of scaling algorithm. Valid choices are:
        'minax': Min-max normalization (the default)
        'standard': Standardization
        'robust' Sklearn's robust scaling
        'none' No scaling
command: string
    Choice of command. Valid choices are:
        'pca': Investigate the effects of component selection on PCA results.
        'silhouette': Produce a silhouette diagram of a dataset given labels.
        'kmeans' Apply k-means++ to cluster the dataset.

PCA Parameters
--------------
threshold : float
    The printing threshold. Only values for n where the percentage of 
    explained variance exceeds this threshold are printed.

Silhouette Parameters
---------------------
k : integer
    The number of clusters.
incol : string
    The name of the column that stores the cluster labels in the 
    data file.

kmeans Parameters
-----------------
k : integer
    The number of clusters to assign.
pca : integer
    The number of PCA components to use.
loadings : file location
    The path to where the PCA loadings should be saved. Does nothing 
    if PCA is not used.
silhouette : flag
    If this flag is present, the script will display the silhouette 
    diagram of the clustering results.
export : file location
    The path to where the newly clustered data file should be saved.
'''

def pca(args, ck, directory):
    ck.investigate_pca(args.threshold)

def silhouette(args, ck, directory):
    preclustering(args, ck)
    ck.labels = ck.rawdata[args.label]
    ck.silhouette(args.k)

def preclustering(args, ck):
    if args.pca:
        ck.pca(args.pca)

def postclustering(args, ck, directory):
    if args.loadings:
        ck.loadings.to_csv(os.path.join(directory, args.loadings), index = False)

    if args.export:
        ck.export(args.export[0]).to_csv(os.path.join(directory, args.export[1]), index = False)

def kmeans(args, ck, directory):
    preclustering(args, ck)
    ck.kmeans(args.k)

    if args.silhouette:
        ck.silhouette(args.k)

    postclustering(args, ck, directory)

def main():
    directory = os.path.dirname(__file__)

    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', help = 'Input file')
    parser.add_argument('columns', help = 'Input columns')
    parser.add_argument('-scaler', help = 'Scaler', default = 'minmax')

    sp = parser.add_subparsers()

    pca_parser = sp.add_parser('pca', help = 'Apply PCA')
    pca_parser.add_argument('-threshold', type = float, default = 0)
    pca_parser.set_defaults(func = pca)

    cluster_parser = argparse.ArgumentParser(add_help = False)
    cluster_parser.add_argument('-pca', help = 'Apply PCA with n components', type = int)
    cluster_parser.add_argument('-loadings', help = 'Export the PCA component loadings')
    cluster_parser.add_argument('-export', nargs = 2, help = 'Export the processed dataset with labels')

    silhouette_parser = sp.add_parser('silhouette', help = 'View silhouette for a cluster assignment', parents = [cluster_parser])
    silhouette_parser.add_argument('k', help = 'Number of clusters assigned', type = int)
    silhouette_parser.add_argument('label', help = 'Cluster label')
    silhouette_parser.set_defaults(func = silhouette)

    kmeans_parser = sp.add_parser('kmeans', help = 'Apply k-means', parents = [cluster_parser])
    kmeans_parser.add_argument('k', help = 'Number of clusters to assign', type = int)
    kmeans_parser.add_argument('-silhouette', help = 'View silhouette', action = 'store_true')
    kmeans_parser.set_defaults(func = kmeans)

    args = parser.parse_args()

    df = pd.read_csv(os.path.join(directory, args.inputfile))

    with open(os.path.join(directory, args.columns)) as f:
        columns = f.read().splitlines()

    ck = ClusterKit(df, columns)

    scalers = {'minmax': preprocessing.MinMaxScaler, 
               'standard': preprocessing.StandardScaler, 
               'robust': preprocessing.RobustScaler}

    if scalers != 'none':
        ck.scale(scalers[args.scaler])

    args.func(args, ck, directory)

if __name__ == "__main__":
    main()