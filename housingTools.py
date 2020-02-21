import pandas as pd
import os
import matplotlib.pyplot as plt

HOUSING_PATH = '/home/awhamil/Downloads'


class Housing:

    def load_housing_data(self, housing_path=HOUSING_PATH):
        csv_path = os.path.join(housing_path, "housing.csv")
        return pd.read_csv(csv_path)

    def plot_hist(self, housing, sess):
        housing.hist(bins=50, figsize=(20, 15))
        fig_path = os.path.join("public/tmp/fig_" + str(sess))
        plt.savefig(fig_path)
        return '/' + fig_path + '.png'
