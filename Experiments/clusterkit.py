import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import matplotlib.cm as cm


'''
Notes
-----
This module contains all of the functions used by cluster_analysis.py,
'''
class ClusterKit:
    '''
    Creates a new cluster kit instance to contain a dataset.

    Parameters
    ----------
    data : dataframe
        The dataframe containing all the data,
    columns : list
        A list of the names of the columns that are to be used as input features.
    '''
    def __init__(self, data, columns):
        self.rawdata = data
        self.columns = columns
        self.datapoints = data[columns]
        self.labels = None
        self.loadings = None

    '''
    Applies a scaling function to the dataset,

    Parameters
    ----------
    function : object
        An sklearn scaling function.
    '''
    def scale(self, function):
        scaler = function()
        self.datapoints = scaler.fit_transform(self.datapoints)

    '''
    Applies k-means++ to the dataset.

    Parameters
    ----------
    n : integer
        The number of clusters to create.
    '''
    def kmeans(self, n):
        kmeans = KMeans(n_clusters = n, random_state = 0, n_init = 10, init = 'k-means++')
        self.labels = kmeans.fit_predict(self.datapoints)

    '''
    Displays a silhouette diagram for the current clustering.

    Parameters
    ----------
    n : integer
        The number of clusters.

    Acknowledgements
    ----------------
    Code from was taken from the sklearn example "Selecting the number of clusters with silhouette analysis on KMeans clustering"
    http://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html#sphx-glr-auto-examples-cluster-plot-kmeans-silhouette-analysis-py
    '''
    def silhouette(self, n):
        silhouette_plot = plt.subplot(111)
        silhouette_plot.set_xlim([-0.1, 1])
        # The (n_clusters+1)*10 is for inserting blank space between silhouette
        # plots of individual clusters, to demarcate them clearly.
        silhouette_plot.set_ylim([0, len(self.datapoints) + (n + 1)*10])

        silhouette_avg = silhouette_score(self.datapoints, self.labels)

        print('For n_clusters =', n, 'The average silhouette_score is :', silhouette_avg)

        sample_silhouette_values = silhouette_samples(self.datapoints, self.labels)

        y_lower = 10

        for i in range(n):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = sample_silhouette_values[self.labels == i]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            cmap = cm.get_cmap('Spectral')
            color = cmap(float(i) / n)
            silhouette_plot.fill_betweenx(np.arange(y_lower, y_upper),
                0, ith_cluster_silhouette_values,
                facecolor = color, edgecolor = color, alpha = 0.7)

            # Label the silhouette plots with their cluster numbers at the middle
            silhouette_plot.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        silhouette_plot.set_xlabel('The silhouette coefficient values')
        silhouette_plot.set_ylabel('Cluster label')

        # The vertical line for average silhouette score of all the values
        silhouette_plot.axvline(x = silhouette_avg, color = 'red', linestyle = '--')

        silhouette_plot.set_yticks([])  # Clear the yaxis labels / ticks
        silhouette_plot.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

        plt.show()

    '''
    Retrieves the dataset with an additional column storing the cluster 
    assignment of each label.

    Parameters
    ----------
    label : string
        The name of the column to store the cluster assignments under.
    '''
    def export(self, label):
        result = pd.DataFrame(self.datapoints)
        result[label] = self.labels
        return result

    '''
    Prints the number of percentage of total variance that can be explained 
    by n PCA components, going from 1 to the total number of features.

    Parameters
    ----------
    threshold : float
        The printing threshold. Only values for n where the percentage of 
        explained variance exceeds this threshold are printed.
    '''
    def investigate_pca(self, threshold = 0):
        pca = PCA()

        pca.fit(self.datapoints)

        total = 0
        i = 0

        for explained in pca.explained_variance_ratio_:
            total += explained
            i += 1

            if total >= threshold:
                print('%s: %s' % (i, total))

    '''
    Applies PCA to the dataset.

    Parameters
    ----------
    n : integer
        The number of PCA components to use.
    '''
    def pca(self, n):
        pca = PCA(n_components = n)
        self.datapoints = pca.fit_transform(self.datapoints)
        loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
        loadings = pd.DataFrame(loadings, columns = list(range(n)))
        loadings['Feature'] = list(self.columns)
        self.loadings = loadings[['Feature'] + list(loadings)[:-1]]