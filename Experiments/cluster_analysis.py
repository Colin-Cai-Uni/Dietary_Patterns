import pandas as pd
import numpy as np
from clusterkit import ClusterKit
from sklearn import preprocessing
import argparse
import os

def pca(args, ck, directory):
    ck.investigate_pca(args.threshold)

def elbow(args, ck, directory):
    preclustering(args, ck)
    ck.elbow(args.n)

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

    elbow_parser = sp.add_parser('elbow', help = 'View elbow plot', parents = [cluster_parser])
    elbow_parser.add_argument('n', help = 'Maximum number of clusters to consider', type = int)
    elbow_parser.set_defaults(func = elbow)

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