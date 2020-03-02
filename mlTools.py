import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import numpy as np
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

LOAD_PATH = 'data'
WORKING_PATH = 'public/tmp'


class MachineLearning:

    def load_csv_as_df(self, sess, working_path=LOAD_PATH):
        x_path = os.path.join(working_path, "data_" + str(sess) + "_X.csv")
        x = pd.read_csv(x_path)
        y_path = os.path.join(working_path, "data_" + str(sess) + "_y.csv")
        y = None
        if os.path.exists(y_path):
            y = pd.read_csv(y_path)
        return [x, y]

    def __save_plot_to_file(self, sess):
        fig_path = os.path.join(WORKING_PATH, "fig_" + str(sess) + '_' + str(int(time.time())))
        plt.savefig(fig_path)
        return '/' + fig_path + '.png'

    def plot_hist(self, df, sess):
        df.hist(bins=50, figsize=(20, 15))
        return self.__save_plot_to_file(sess)

    def scatter_plot(self, sess, x_df, y_df=None):
        tmp_df = pd.DataFrame(data=x_df.loc[:, 0:1], index=x_df.index)
        if y_df is not None:
            tmp_df = pd.concat((tmp_df, y_df), axis=1, join='inner')
            tmp_df.columns = ['x', 'y', 'c']
            plt.scatter(x=tmp_df['x'], y=tmp_df['y'], c=tmp_df['c'])
            plt.legend()
        else:
            tmp_df.columns = ['x', 'y']
            plt.scatter(x=tmp_df['x'], y=tmp_df['y'])
        return self.__save_plot_to_file(sess)

    def tsne_lite(self, x_df, max_row=5000, max_col=9):
        t_sne = TSNE()
        return pd.DataFrame(data=t_sne.fit_transform(x_df.loc[:max_row, :max_col]), index=x_df.index[:max_row + 1])

    def tsne(self, x_df, max_col=9):
        t_sne = TSNE()
        return pd.DataFrame(data=t_sne.fit_transform(x_df.loc[:, :max_col]), index=x_df.index)

    def pca(self, df):
        pca = PCA(n_components=min(df.shape[0], df.shape[1]))
        df_pca = pd.DataFrame(data=pca.fit_transform(df), index=df.index)
        component_importance = pd.DataFrame(data=pca.explained_variance_ratio_).T
        variance = ['Variance of first 10 components: ' + str(component_importance.loc[:, 0:9].sum(axis=1).values),
                    'Variance of first 20 components: ' + str(component_importance.loc[:, 0:19].sum(axis=1).values),
                    'Variance of first 50 components: ' + str(component_importance.loc[:, 0:49].sum(axis=1).values),
                    'Variance of first 100 components: ' + str(component_importance.loc[:, 0:99].sum(axis=1).values),
                    'Variance of first 200 components: ' + str(component_importance.loc[:, 0:199].sum(axis=1).values),
                    'Variance of first 300 components: ' + str(component_importance.loc[:, 0:299].sum(axis=1).values)]
        return [df_pca, variance]

    def kmeans(self, df, k):
        k_means = KMeans(n_clusters=k)

        # distribution showing each sample and how close it is to each cluster
        dist = k_means.fit_transform(df)
        dist_df = pd.DataFrame(data=dist, index=df.index)

        # the labels, one per sample, showing to which cluster the sample has been assigned
        labels_df = pd.DataFrame(data=k_means.labels_, index=df.index)

        # for each cluster, the one sample that is closest to the cluster centroid
        best_reps_idx = np.argmin(dist, axis=0)
        best_reps_df = df.iloc[best_reps_idx]
        best_reps_labels = labels_df.iloc[best_reps_idx]

        # for each cluster, the 20% of the samples that are closest to the cluster centroid
        percentile_closest = 20
        x_cluster_dist = dist[np.arange(len(df)), k_means.labels_]
        for i in range(k):
            in_cluster = (k_means.labels_ == i)
            cluster_dist = x_cluster_dist[in_cluster]
            cutoff_distance = np.percentile(cluster_dist, percentile_closest)
            above_cutoff = (x_cluster_dist > cutoff_distance)
            x_cluster_dist[in_cluster & above_cutoff] = -1
        best_20_index = (x_cluster_dist != -1)
        best_20_df = df[best_20_index]
        best_20_labels_df = labels_df[best_20_index]

        # the cluster centroids
        clusters_df = pd.DataFrame(data=k_means.cluster_centers_)

        return {'labels': labels_df, 'dist': dist_df, 'best_reps': best_reps_df, 'clusters': clusters_df,
                'best20': best_20_df, 'best20labels': best_20_labels_df, 'best_reps_labels': best_reps_labels}

    @staticmethod
    def cat2int(df, col_name):
        def tokenizer(text):
            return [text]

        vectorizer = CountVectorizer(tokenizer=tokenizer)
        v = vectorizer.fit_transform(df[col_name])
        vocab = vectorizer.vocabulary_
        new_cols_df = pd.DataFrame(data=v.toarray(), columns=sorted(vocab, key=vocab.get), index=df.index)
        return pd.concat((df.drop(columns=col_name), new_cols_df), axis=1, join='inner')
        # pipeline = ColumnTransformer(transformers=[('cat', OneHotEncoder(), [col_name])], remainder='passthrough')
        # return pd.DataFrame(data=pipeline.fit_transform(df), index=df.index)

    @staticmethod
    def feature_scale(df):
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy="median")),
            ('std_scaler', StandardScaler())
        ])
        return pd.DataFrame(data=pipeline.fit_transform(df), index=df.index, columns=df.columns)
