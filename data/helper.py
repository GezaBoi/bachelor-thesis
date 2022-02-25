from typing import Tuple, Any

import pandas as pd

CACHE_PATH = "data/cache/"


def load_df_cache(file_path: str) -> Tuple[bool, pd.DataFrame]:
    try:
        df = pd.read_pickle(CACHE_PATH + file_path)
        success = True
    except FileNotFoundError:
        df = pd.DataFrame()
        success = False
    return success, df


def save_df_cache(df: pd.DataFrame, file_path: str) -> None:
    df.to_pickle(CACHE_PATH + file_path, protocol=4)


def load_csv(path: str) -> Tuple[bool, pd.DataFrame]:
    try:
        df = pd.read_csv(path)
        if "time" in df.columns:
            df.set_index("time", inplace=True)
        return True, df
    except FileNotFoundError:
        return False, pd.DataFrame()


def load_pickle(path: str) -> Tuple[bool, pd.DataFrame]:
    try:
        df = pd.read_csv(path)
        return True, df
    except FileNotFoundError:
        return False, pd.DataFrame()
