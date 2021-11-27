from typing import cast
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def create_linear_regression_model(data: pd.Series) -> LinearRegression:
    x = data.index.view(np.int64).reshape((-1, 1))
    y = data.values
    model = LinearRegression()
    model = model.fit(x, y)
    return cast(LinearRegression, model)


def predict_linear_regression_model(
    model: LinearRegression, timestamps: pd.Index
) -> pd.Series:
    x = timestamps.view(np.int64).reshape((-1, 1))
    prediction = pd.Series(data=model.predict(x), index=timestamps)
    return prediction


if __name__ == "__main__":
    from data import get_forecast_data, get_extrapolation_data
    import pandas as pd

    forecast_df = get_forecast_data()
    forecast_df["total"] = forecast_df.sum(axis=1)

    model = create_linear_regression_model(forecast_df["total"])
    forecast_df["total_linear_prediction"] = predict_linear_regression_model(
        model, forecast_df.index
    )

    pd.options.plotting.backend = "plotly"
    fig = forecast_df[["total", "total_linear_prediction"]].resample("1D").sum().plot()
    fig.show()
