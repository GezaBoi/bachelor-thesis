# source: https://www.sciencedirect.com/science/article/pii/S2211467X20300778

from scipy.fft import fft, fftfreq
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

if __name__ == "__main__":
    from data import get_forecast_data, get_extrapolation_data

    extrapolation_df = get_extrapolation_data()
    extrapolation_df["total"] = extrapolation_df.sum(axis=1)

    N = len(extrapolation_df)
    SAMPLE_RATE = 24 * 4  # samples per day

    yf = fft(extrapolation_df.total.values)
    xf = fftfreq(N, 1 / SAMPLE_RATE)

    df = pd.DataFrame(index=xf, data=np.abs(yf))
    plt.plot(xf, np.abs(yf))
    plt.show()

    import pandas as pd
    import statsmodels.api as sm

    extrapolation_df = get_extrapolation_data()

    extrapolation_df["total"] = extrapolation_df.sum(axis=1)
    extrapolation_df["total"] = (
        extrapolation_df["total"] - extrapolation_df["total"].mean()
    )

    extrapolation_df = extrapolation_df.resample("1h").sum()
    res = sm.tsa.seasonal_decompose(extrapolation_df.total)
    resplot = res.plot()

    # N = len(extrapolation_df)
    #
    # pd.options.plotting.backend = "plotly"
    # df = extrapolation_df[["total"]].resample("1D").sum()
    # # df["total_sma"] = df[["total"]].rolling(30).mean()
    # fig = df.plot()
    # fig.show()
