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

def preclustering(args, ck):
    if args.pca:
        ck.pca(args.pca)

def postclustering(args, ck, directory):
    if args.export:
        ck.export().to_csv(os.path.join(directory, args.export))

def kmeans(args, ck, directory):
    preclustering(args, ck)
    ck.kmeans(args.k)

    if args.silhouette:
        ck.silhouette(args.k)

    # if args.sse:
        # Get -score from ck

    postclustering(args, ck, directory)

def optics(args, ck, directory):
    preclustering(args, ck)
    ck.optics(args.eps, args.minpts, args.clusters)
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
    cluster_parser.add_argument('-export', help = 'Export the results')

    elbow_parser = sp.add_parser('elbow', help = 'View elbow plot', parents = [cluster_parser])
    elbow_parser.add_argument('n', type = int)
    elbow_parser.set_defaults(func = elbow)

    kmeans_parser = sp.add_parser('kmeans', help = 'Apply k-means', parents = [cluster_parser])
    kmeans_parser.add_argument('k', type = int)
    kmeans_parser.add_argument('-silhouette', help = 'View silhouette', action = 'store_true')
    kmeans_parser.add_argument('-sse', help = 'View sum of squared error', action = 'store_true')
    kmeans_parser.set_defaults(func = kmeans)

    optics_parser = sp.add_parser('optics', help = 'Apply OPTICS', parents = [cluster_parser])
    optics_parser.add_argument('eps', type = float)
    optics_parser.add_argument('minpts', type = int)
    optics_parser.add_argument('-clusters', help = 'Manually specify a number of clusters', type = int, default = None)
    optics_parser.set_defaults(func = optics)

    args = parser.parse_args()

    inputfile = pd.read_csv(os.path.join(directory, args.inputfile))

    with open(os.path.join(directory, args.columns)) as f:
        columns = f.read().splitlines()

    ck = ClusterKit(inputfile, columns)

    scalers = {'minmax': preprocessing.MinMaxScaler, 
               'standard': preprocessing.StandardScaler, 
               'robust': preprocessing.RobustScaler}

    ck.scale(scalers[args.scaler])

    args.func(args, ck, directory)

if __name__ == "__main__":
    main()