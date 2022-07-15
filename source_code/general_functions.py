import re
import pandas as pd
from typing import Tuple


def get_date(link: str) -> Tuple[int, int]:
    """Returns the years from when the data is available.

    Args:
        link (str): the link that has included the dails for the available data time

    Returns:
        Tuple[int,int]: start time, end time
    """
    m = re.findall("\d{8}", link)
    if m:
        return (int(m[0][:4]), int(m[1][:4]))
    return (0, 0)


def select_time_range(df: pd.DataFrame, start_dd_mm: str, end_dd_mm: str):
    # Step 1: create the time intervals from the input "dd.mm"
    month_start = int(start_dd_mm.split(".")[1])
    month_end = int(end_dd_mm.split(".")[1])
    day_start = int(start_dd_mm.split(".")[0])
    day_end = int(end_dd_mm.split(".")[0])
    if month_start == month_end:
        months = [month_start]
    elif month_start < month_end:
        months = [i for i in range(month_start, month_end + 1, 1)]
    else:
        months = [i for i in range(month_start, 13, 1)] + [
            i for i in range(1, month_end + 1, 1)
        ]

    # Step 2: clean the dataframe with the created time intervals
    df = df[df["month"].isin(months)]  # first the months
    df.drop(
        df[(df["month"] == month_start) & (df["day"] < day_start)].index, inplace=True
    )  # then take out the not included days from the first month
    df.drop(
        df[(df["month"] == month_end) & (df["day"] > day_end)].index, inplace=True
    )  # then those from the last month
    return df
