import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from pyclustering.cluster import optics
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.neighbors import NearestNeighbors
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
from mpl_toolkits.mplot3d import axes3d, Axes3D

class ClusterKit:
    def __init__(self, data, columns):
        self.rawdata = data
        self.datapoints = data[columns]
        self.labels = None

    def scale(self, function):
        scaler = function()
        self.datapoints = scaler.fit_transform(self.datapoints)

    def kmeans(self, n):
        kmeans = KMeans(n_clusters = n, random_state = 0, n_init = 10, init = 'k-means++')
        self.labels = kmeans.fit_predict(self.datapoints)

    # Code from http://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html#sphx-glr-auto-examples-cluster-plot-kmeans-silhouette-analysis-py
    def silhouette(self, n):
        silhouette_plot = plt.subplot(111)
        silhouette_plot.set_xlim([-0.1, 1])
        # The (n_clusters+1)*10 is for inserting blank space between silhouette
        # plots of individual clusters, to demarcate them clearly.
        silhouette_plot.set_ylim([0, len(self.datapoints) + (n + 1) * 10])

        silhouette_avg = silhouette_score(self.datapoints, self.labels)

        print("For n_clusters =", n, "The average silhouette_score is :", silhouette_avg)

        sample_silhouette_values = silhouette_samples(self.datapoints, self.labels)

        y_lower = 10

        for i in range(n):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = sample_silhouette_values[self.labels == i]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            cmap = cm.get_cmap("Spectral")
            color = cmap(float(i) / n)
            silhouette_plot.fill_betweenx(np.arange(y_lower, y_upper),
                0, ith_cluster_silhouette_values,
                facecolor=color, edgecolor=color, alpha=0.7)

            # Label the silhouette plots with their cluster numbers at the middle
            silhouette_plot.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        silhouette_plot.set_title("The silhouette plot for the various clusters.")
        silhouette_plot.set_xlabel("The silhouette coefficient values")
        silhouette_plot.set_ylabel("Cluster label")

        # The vertical line for average silhouette score of all the values
        silhouette_plot.axvline(x=silhouette_avg, color="red", linestyle="--")

        silhouette_plot.set_yticks([])  # Clear the yaxis labels / ticks
        silhouette_plot.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

        plt.show()

    def optics(self, eps, minpts, amount_clusters = None):
        clusterer = optics.optics(self.datapoints, eps, minpts, amount_clusters)
        clusterer.process()
        clusters = clusterer.get_clusters()
        clusters.append(clusterer.get_noise())
        n_clusters = len(clusters)
        self.labels = np.empty(np.shape(self.datapoints)[0])

        for i in range(np.shape(self.datapoints)[0]):
            for c in range(n_clusters):
                if i in clusters[c]:
                    self.labels[i] = c
                    break

        # Split this off sometime
        ordering = optics.ordering_analyser(clusterer.get_ordering())
        optics.ordering_visualizer.show_ordering_diagram(ordering)

    def export(self):
        self.rawdata['cluster'] = self.labels
        return self.rawdata

    def export_scaled(self):
        result = pd.DataFrame(self.datapoints)
        result['cluster'] = self.labels
        return result

    def agglomerative(self, n, method):
        links = linkage(self.datapoints, method)
        clusters = []

        for i in range(np.shape(self.datapoints)[0]):
            clusters.append([i])

        for l in links[:-n + 1]:
            clusters.append(clusters[int(l[0])] + clusters[int(l[1])])
            clusters[int(l[0])] = None
            clusters[int(l[1])] = None

        self.labels = np.zeros((np.shape(self.datapoints)[0],))

        cluster_number = 0

        for c in clusters:
            if c:
                for point in c:
                    self.labels[point] = cluster_number

                cluster_number += 1

        #plt.figure()
        #dn = dendrogram(links, p = 5, truncate_mode = 'level')
        #plt.show()

    def investigate_pca(self, threshold = 0):
        pca = PCA()

        pca.fit(self.datapoints)

        total = 0
        i = 0

        for explained in pca.explained_variance_ratio_:
            total += explained
            i += 1

            if total >= threshold:
                print("%s: %s" % (i, total))

    def pca(self, n):
        pca = PCA(n_components = n)
        self.datapoints = pca.fit_transform(self.datapoints)

    def elbow(self, n):
        instances = [KMeans(n_clusters = i) for i in range(1, n)]
        scores = [-instance.fit(self.datapoints).score(self.datapoints) for instance in instances]
        plt.plot(range(1, n), scores)
        plt.xticks(range(1, n))
        plt.show()