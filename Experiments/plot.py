import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os

'''
A script to plot the tabulated results of a clustering experiment.
Each plot has a corresponding tabulated summary.

Parameters
----------
inputfile : file location
    Location of the clustering results.
bar_columns : file location
    Location of a file listing the columns to be output as bar plots 
    with each column on a new line.
box_columns : file location
    Location of a file listing the columns to be output as box plots 
    with each column on a new line.
cluster_column : string
    The name of the column that encodes the cluster labels. If absent, 
    this script will output the general plots of the input file as a whole
    as if it were a single cluster.
outputfolder : directory location
    Location of the directory to place all the plots and summaries.
'''
def main():
    directory = os.path.dirname(__file__)

    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', help = 'Input file')
    parser.add_argument('-bar_columns', help = 'Bar plot output columns')
    parser.add_argument('-box_columns', help = 'Box plot output columns')
    parser.add_argument('-cluster_column', help = 'Cluster column')
    parser.add_argument('outputfolder', help = 'Output folder')

    args = parser.parse_args()

    data = pd.read_csv(open(os.path.join(directory, args.inputfile)))

    if not args.cluster_column:
        data['cluster'] = 0
        args.cluster_column = 'cluster'

    box_columns = []
    bar_columns = []

    if args.box_columns:
        with open(os.path.join(directory, args.box_columns)) as f:
            box_columns = f.read().splitlines()

    if args.bar_columns:
        with open(os.path.join(directory, args.bar_columns)) as f:
            bar_columns = f.read().splitlines()

    labels = np.unique(data[args.cluster_column].values)
    labels.sort()

    destination = args.outputfolder + ('/%s plot.%s')

    # Create the population plot
    populations = data[args.cluster_column].value_counts(sort = False).sort_index().values
    plt.bar(labels, populations)
    plt.xticks(labels)
    plt.savefig(os.path.join(directory, destination % ('population', 'png')))
    plt.close()

    tlabels = [str(l) for l in labels]

    # Create the population summary
    with open(os.path.join(directory, destination % ('population', 'csv')), 'w+') as f:
        f.write('cluster,%s\n' % (','.join(tlabels)))
        f.write('%s,%s\n' % ('count', ','.join(populations.astype(str))))

    # Create the bar plots
    for c in bar_columns:
        barplot(c, args.cluster_column, data, labels, directory, destination)

    # Create the box plots
    with open(os.path.join(directory, destination % ('summary', 'csv')), 'w+') as f:
        f.write('cluster,%s\n' % (','.join(tlabels)))

        for c in box_columns:
            cluster_data = []

            for l in labels:
                cluster_data.append(data[data[args.cluster_column] == l][c])

            # Create a summary file for all the box plot columns
            summary = boxplot(c, cluster_data, labels, directory, destination)
            f.write('%s,%s\n' % (''.join(c.split(',')),
                    ','.join(['%s (%s)' % (summary[0][i], summary[1][i]) for i in range(len(labels))])))

'''
Creates and exports a boxplot and boxplot summary of the clusters for a given column.

Parameters
----------
column : string
    Name of the column.
data : list of numpy arrays
    A list of the column values for each cluster.
data : array_like
    A structure containing the names of the clusters.
directory : string
    The output directory.
directory : string
    The destination filename template.

Returns
-------
table : list of lists
    A list of the means and standard deviations for each cluster.
'''
def boxplot(column, data, labels, directory, destination):
    # Produce the plot
    fig, ax = plt.subplots(1)

    results = ax.boxplot(data)
    ax.set_xticklabels(labels)

    table = [[None for _ in range(len(labels))] for _ in range(7)]

    # Extract details from the plot's graphing parameters to place into the summary file
    for l in labels:
        table[0][l] = format(np.mean(data[l].values))
        table[1][l] = format(np.std(data[l].values))

        lower = results['whiskers'][2*l].get_ydata()
        table[2][l] = format(lower[1])
        table[3][l] = format(lower[0])

        table[4][l] = format(results['medians'][l].get_ydata()[0])

        upper = results['whiskers'][2*l + 1].get_ydata()
        table[5][l] = format(upper[0])
        table[6][l] = format(upper[1])

    plt.savefig(os.path.join(directory, destination % (column, 'png')))
    plt.close()

    # Produce the summary file
    with open(os.path.join(directory, destination % (column, 'csv')), 'w+') as f:
        labels = [str(l) for l in labels]
        f.write('cluster,%s\n' % (','.join(labels)))

        rows = ['Mean', 'Standard Deviation', 'Minimum', 'First Quartile', 'Median', 'Third Quartile', 'Maximum']

        for i in range(len(rows)):
            f.write('%s,%s\n' % (rows[i], ','.join(table[i])))

    return table[0:2]

'''
Creates and exports a barplot and barplot summary of the clusters for a given column.

Parameters
----------
column : string
    Name of the column.
data : dataframe
    The dataframe of the clustering results.
data : array_like
    A structure containing the names of the clusters.
directory : string
    The output directory.
directory : string
    The destination filename template.
'''
def barplot(column, cluster, data, labels, directory, destination):
    counts = []

    for l in labels:
        count = data[data[cluster] == l][column].value_counts().sort_index().rename(l)
        count = count/count.sum()
        counts.append(count)

    is_cluster = 'cluster' if len(labels) > 1 else None

    # Produce the plot
    counts = pd.concat(counts, axis = 1).reset_index().rename(columns = {'index': 'value'})
    counts.fillna(0, inplace = True)

    values = counts['value'].values

    plot_counts = pd.melt(counts, id_vars = 'value', var_name = is_cluster, value_name = 'proportion')

    fig = sns.catplot(x = 'value', y = 'proportion', hue = is_cluster, data = plot_counts, 
                      kind = 'bar')

    ax = plt.gca()
    ax.set_ylim([0, 1])

    plt.savefig(os.path.join(directory, destination % (column, 'png')))
    plt.close()

    # Produce the summary file
    for l in labels:
        counts[l] = counts[l].apply(format)

    counts.to_csv(os.path.join(directory, destination % (column, 'csv')), index = False)

def format(x):
    return '%.4f' % (round(x, 4))

if __name__ == "__main__":
    main()