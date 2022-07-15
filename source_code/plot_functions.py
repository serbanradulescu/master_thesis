import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from typing import List
from source_code.general_functions import select_time_range


def plot_optimal_temperature(
    df: pd.DataFrame,
    temp_min: float,
    temp_max: float,
    hist_start: float,
    hist_end: float,
    start_dd_mm: str,
    end_dd_mm: str,
    moving_average: int,
):
    """Creates the plot for the optimal temperature

    Args:
        df (pd.DataFrame): the dataframe with hourly temperature
        temp_min (float): minimum of temperature interval
        temp_max (float): maximum of temperature interval
        hist_start (float): start of the reference period
        hist_end (float): end of the reference period
        start_dd_mm (str): start date in the dd.mm format
        end_dd_mm (str): end date in the dd.mm format
        moving_average (int): the number of years for the moving average (e.g.7)
    """

    # Step 1: create the time intervals from the input "dd.mm"
    df = select_time_range(df, start_dd_mm=start_dd_mm, end_dd_mm=end_dd_mm)
    # Step 2: apply the function
    df["useful_t"] = df.TT_TU.apply(
        lambda x: 1 if (x >= temp_min and x <= temp_max) else 0
    )

    # Step 3: process and prepare for plotting
    df = df.groupby(["year"]).mean()
    avg_hist = df[(df.index <= hist_end) & (df.index >= hist_start)]["useful_t"].mean()
    max_hist = df[(df.index <= hist_end) & (df.index >= hist_start)]["useful_t"].max()
    min_hist = df[(df.index <= hist_end) & (df.index >= hist_start)]["useful_t"].min()
    df[f"{moving_average}years_average"] = df.useful_t.rolling(moving_average).mean()

    # Step 4: plot
    plt.figure(figsize=(15, 8))
    sns.lineplot(
        x="year", y="useful_t", data=df, label="yearly optimal hours %", alpha=0.55
    )
    sns.lineplot(
        x="year",
        y=f"{moving_average}years_average",
        data=df,
        label=f"{moving_average} years average",
        color="orange",
    )
    sns.lineplot(
        x=df.index,
        y=min_hist,
        linestyle="dashed",
        label=f"minimum in the historical period ({hist_start}-{hist_end})",
    )
    sns.lineplot(
        x=df.index,
        y=avg_hist,
        linestyle="dashed",
        label=f"average in the historical period ({hist_start}-{hist_end})",
    )
    sns.lineplot(
        x=df.index,
        y=max_hist,
        linestyle="dashed",
        label=f"maximum period in the historical period ({hist_start}-{hist_end})",
    )
    plt.ylabel("% of hours with optimal temperature")
    # plt.plot([hist_end,hist_end], [-0.00,0.05], lw=2, color = "0.65", label = "historical period (left)")

    plt.figtext(
        0.15,
        0.021,
        f"""Figure 1. Variation of optimal temperature % for Septoria tritici in Germany from 1950 - 2020 compared to the reference period of ({hist_start} - {hist_end}). Optimal temperature 
        \n is considered when air  temperature is between {temp_min} and {temp_max} degrees Celsius. The yearly time range is between sowing of wheat and harvesting in Germany, which is considered: {start_dd_mm} - {end_dd_mm},
        \n corresponding to the interval when 90% of the crop was is in that stage """,
    )
    plt.show()


def plot_lw_RHt(
    df: pd.DataFrame,
    thresholds: List[float],
    hist_start: float,
    hist_end: float,
    start_dd_mm: str,
    end_dd_mm: str,
    moving_average: int,
    hours: List[int],
):

    # Step 1: create the time intervals from the input "dd.mm"
    df = select_time_range(df, start_dd_mm=start_dd_mm, end_dd_mm=end_dd_mm)
    # Step 2: apply the function
    for i in thresholds:
        df[f"lw{i}"] = df["RF_STD"].apply(lambda x: 1 if float(x) >= i else 0)

    # Step 3: process and prepare for plotting
    df = df.groupby("year").mean()
    for i in thresholds:
        df[f"lw{i}_7years_average"] = df[f"lw{i}"].rolling(moving_average).mean()
        df[f"avg_hist_lw{i}"] = df[(df.index >= hist_start) & (df.index <= hist_end)][
            f"lw{i}"
        ].mean()

    # Step 4: plot
    plt.figure(figsize=(15, 7.5))
    for i in thresholds:
        sns.lineplot(
            x="year",
            y=f"lw{i}",
            data=df,
            label=f"leaf humidity treshold set at RH = {i}",
            alpha=0.33,
        )
        sns.lineplot(
            x="year", y=f"lw{i}_7years_average", data=df, label=f"lw{i}_7years_average"
        )
        sns.lineplot(
            x="year",
            y=f"avg_hist_lw{i}",
            data=df,
            linestyle="dashed",
            label=f"{moving_average} years moving average for lw{i}",
        )
    plt.title(
        f"Leaf wetness for different RH treshold measured in the interval {hours}"
    )
    plt.figtext(
        0.15,
        0.031,
        f"Fig 4. Leaf wetness events from RH leaf wetness model applied for different RH tresholds on data from 1950 - 2019  in Germany.",
    )
    plt.show()


def plot_lw_dpd(
    df,
    start_dd_mm: str,
    end_dd_mm: str,
):

    # Step 1: create the time intervals from the input "dd.mm"
    df = select_time_range(df, start_dd_mm=start_dd_mm, end_dd_mm=end_dd_mm)

    # Step 2: apply the function
    df["difference"] = df.apply(lambda x: (x["TT"] - x["TD"]), axis=1)

    # Step 3: process and prepare for plotting
    df = df.groupby("year").mean()
    avg50_79 = df[df.index <= 1979]["difference"].mean()
    max50_79 = df[df.index <= 1979]["difference"].max()
    min50_79 = df[df.index <= 1979]["difference"].min()
    df["7yrs_average"] = df.difference.rolling(7).mean()

    # Step 4: plot
    plt.figure(figsize=(15, 8))
    sns.lineplot(
        x=df.index, y=df["difference"]
    )  # , label = "average yearly difference")
    sns.lineplot(
        x=df.index, y=df["7yrs_average"], label="7 years average", color="orange"
    )
    sns.lineplot(
        x=df.index,
        y=min50_79,
        linestyle="dashed",
        label="minimum in the historical period (1950-1979)",
    )
    sns.lineplot(
        x=df.index,
        y=avg50_79,
        linestyle="dashed",
        label="average in the historical period (1950-1979)",
    )
    sns.lineplot(
        x=df.index,
        y=max50_79,
        linestyle="dashed",
        label="maximum perios in the historical period (1950-1979)",
    )

    plt.figtext(
        0.15,
        0.021,
        "Figure 3. Variation of leaf wetness determined trough dew point difference % for Septoria tritici in Germany in the time period of 1950 - 2020. Optimal temperature is considered when air \n temperature is between 15 and 25 degrees Celsius in the months of Decemvber to April. ",
    )
    plt.show()


def plot_dryness(df, start_dd_mm: str, end_dd_mm: str, treshhold: float = 70):

    # Step 1: create the time intervals from the input "dd.mm"
    df = select_time_range(df, start_dd_mm=start_dd_mm, end_dd_mm=end_dd_mm)

    # Step 2: apply the function
    df[f"dry_leaf"] = df["RF_STD"].apply(lambda x: 1 if float(x) <= treshhold else 0)

    # Step 3: process and prepare for plotting
    df = df.groupby("year").mean()
    df["7yrs_average"] = df.dry_leaf.rolling(7).mean()
    avg50_79 = df[df.index <= 1979]["dry_leaf"].mean()

    # Step 3: plot
    plt.figure(figsize=(15, 7))
    sns.lineplot(
        x=df.index, y=avg50_79, label="historical (1950-1979) average dry leaf"
    )
    sns.lineplot(x="year", y="dry_leaf", data=df, label="yearly dry leaf")
    sns.lineplot(x="year", y="7yrs_average", data=df, label="7 years average dry leaf")
    plt.title(f"Leaf dryness for RH = {treshhold} threshhold")
    plt.ylabel("% of hours with leaf dryness")
    plt.figtext(
        0.15,
        0.031,
        f"Fig 5. Leaf dryness events from RH leaf wetness model applied for treshold {treshhold} on data from 1950 - 2019  in Germany.",
    )
    plt.show()
