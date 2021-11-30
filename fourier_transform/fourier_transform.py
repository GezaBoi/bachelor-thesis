# source: https://gist.github.com/tartakynov/83f3cd8f44208a1856ce
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np
import pylab as pl
from numpy import fft, nan


def fourier_transform(
    data: pd.Series, predict_until: datetime, n_harm: int
) -> pd.Series:
    x = data.values
    n = data.size
    t = np.arange(0, n)
    p = np.polyfit(t, x, 1)  # find linear trend in x
    data_range = pd.date_range(
        start=data.index.min(), end=predict_until, freq=data.index.freq
    )
    n_predict = len(data_range.difference(data.index))
    x_notrend = x - p[0] * t  # detrended x
    x_freqdom = fft.fft(x_notrend)  # detrended x in frequency domain
    f = fft.fftfreq(n)  # frequencies
    indexes = list(range(n))
    # sort indexes by frequency, lower -> higher
    indexes.sort(key=lambda i: np.absolute(f[i]))

    t = np.arange(0, n + n_predict)
    restored_sig = np.zeros(t.size)
    for i in indexes[: 1 + n_harm * 2]:
        ampli = np.absolute(x_freqdom[i]) / n  # amplitude
        phase = np.angle(x_freqdom[i])  # phase
        restored_sig += ampli * np.cos(2 * np.pi * f[i] * t + phase)

    fourier_extrapolation = restored_sig + p[0] * t
    fourier_series = pd.Series(
        index=data_range, data=fourier_extrapolation, name="fourier_extrapolation"
    )
    return fourier_series


if __name__ == "__main__":
    from data import get_forecast_data, get_extrapolation_data

    extrapolation_df = get_extrapolation_data()

    extrapolation_df["total"] = extrapolation_df.sum(axis=1)
    extrapolation_df = extrapolation_df.resample("1D").sum()
    extrapolation_df = extrapolation_df.loc[
        extrapolation_df.index
        >= datetime(year=2012, month=1, day=1, tzinfo=timezone.utc)
    ]

    x = extrapolation_df["total"].values
    n_predict = 365
    extrapolation = fourier_transform(
        x,
        n_predict,
    )

    start_date = extrapolation_df.index.min()
    end_date = extrapolation_df.index.max() + timedelta(days=n_predict)

    df = pd.DataFrame(
        index=pd.date_range(start=start_date, end=end_date, freq="1D", tz="UTC"),
        data={
            "x": list(x) + [nan for _ in range(n_predict)],
            "extrapolation": extrapolation,
        },
    )

    pd.options.plotting.backend = "plotly"
    fig = df.plot()
    fig.show()
