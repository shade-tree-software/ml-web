import pandas as pd
import os

HOUSING_PATH = '/home/awhamil/Downloads'


class Housing:

    def load_housing_data(self, housing_path=HOUSING_PATH):
        csv_path = os.path.join(housing_path, "housing.csv")
        return pd.read_csv(csv_path)
