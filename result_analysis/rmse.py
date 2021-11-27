from sklearn import preprocessing
from statsmodels.tools.eval_measures import rmse
import numpy as np


def normalized_rmse(x: np.array, y: np.array) -> float:
    min_max_scaler_x = preprocessing.MinMaxScaler()
    x_transposed = x.reshape(-1, 1)
    x_min_max_scaler = min_max_scaler_x.fit(x_transposed)
    x_normalized = x_min_max_scaler.fit_transform(x_transposed)

    min_max_scaler_y = preprocessing.MinMaxScaler()
    y_transposed = y.reshape(-1, 1)
    y_min_max_scaler = min_max_scaler_y.fit(y_transposed)
    y_normalized = y_min_max_scaler.fit_transform(y_transposed)

    error = rmse(x_normalized.T[0], y_normalized.T[0])
    return error
