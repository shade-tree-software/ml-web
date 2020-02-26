import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import numpy as np

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
        fig_path = os.path.join(WORKING_PATH, "fig_" + str(sess))
        plt.savefig(fig_path)
        return '/' + fig_path + '.png'

    def plot_hist(self, df, sess):
        df.hist(bins=50, figsize=(20, 15))
        return self.__save_plot_to_file(sess)

    def __scatter_plot(self, x_df, y_df=None):
        tmp_df = pd.DataFrame(data=x_df.loc[:, 0:1], index=x_df.index)
        if y_df is not None:
            tmp_df = pd.concat((tmp_df, y_df), axis=1, join='inner')
            tmp_df.columns = ['First Vector', 'Second Vector', 'Label']
            sns.lmplot(x='First Vector', y='Second Vector', hue='Label', data=tmp_df, fit_reg=False)
        else:
            tmp_df.columns = ['First Vector', 'Second Vector']
            sns.lmplot(x='First Vector', y='Second Vector', data=tmp_df, fit_reg=False)

    def plot_tsne(self, x_df, y_df, sess, max_row=5000, max_col=9):
        tsne = TSNE()
        x_df_tsne = pd.DataFrame(data=tsne.fit_transform(x_df.loc[:max_row, :max_col], x_df.index[:max_row + 1]))
        self.__scatter_plot(x_df_tsne, y_df)
        return self.__save_plot_to_file(sess)

    def pca(self, df):
        pca = PCA(n_components=df.shape[1])
        df_pca = pd.DataFrame(data=pca.fit_transform(df), index=df.index)
        component_importance = pd.DataFrame(data=pca.explained_variance_ratio_).T
        variance = ['Variance of first 10 components: ' + str(component_importance.loc[:, 0:9].sum(axis=1).values),
                    'Variance of first 20 components: ' + str(component_importance.loc[:, 0:19].sum(axis=1).values),
                    'Variance of first 50 components: ' + str(component_importance.loc[:, 0:49].sum(axis=1).values),
                    'Variance of first 100 components: ' + str(component_importance.loc[:, 0:99].sum(axis=1).values),
                    'Variance of first 200 components: ' + str(component_importance.loc[:, 0:199].sum(axis=1).values),
                    'Variance of first 300 components: ' + str(component_importance.loc[:, 0:299].sum(axis=1).values)]
        return [df_pca, variance]

    def k_means(self, df):
        kmeans = KMeans(n_clusters=10)
        dist = kmeans.fit_transform(df)
        idx = np.argmin(dist, axis=0)
        labels_df = pd.DataFrame(data=kmeans.labels_, index=df.index)
        return [labels_df, df.iloc[idx]]
