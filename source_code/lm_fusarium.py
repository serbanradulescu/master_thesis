from scipy.stats import linregress
from scipy import stats
import pandas as pd

from source_code.general_functions import select_time_range


def linear_model_temperature(
    df_airtemp: pd.DataFrame,
    start_dd_mm: str,
    end_dd_mm: str,
    func,
    year_minus: int = 0,
):
    results = pd.DataFrame(
        columns=[
            "station id",
            "r_value",
            "gradient",
            "intercept",
            "p_value",
            "conclusion",
        ]
    )
    df = df_airtemp.copy()
    for station in df.STATIONS_ID.unique():
        save_station = station
        df = df_airtemp.copy()
        df = df[df["STATIONS_ID"] == station]
        df = select_time_range(df, start_dd_mm=start_dd_mm, end_dd_mm=end_dd_mm)
        df["useful_t"] = df.TT_TU.apply(func)

        df = df.groupby(["year"]).mean().reset_index()

        x = [i - year_minus for i in df.year]
        y = df.useful_t
        gradient, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        if p_value < 0.05 and gradient > 0:
            verdict = "significant"
        elif p_value < 0.05 and gradient < 0:
            verdict = "significant but decreasing risk"
        else:  # p_value > 0.05:
            verdict = "non-significant"

        results_new_row = pd.DataFrame(
            {
                "station id": [save_station],
                "r_value": [r_value],
                "gradient": [gradient],
                "intercept": [intercept],
                "p_value": [p_value],
                "conclusion": [verdict],
            }
        )
        results = pd.concat([results, results_new_row], ignore_index=True)
    return results


def linear_model_moisture(
    df_moisture: pd.DataFrame,
    start_dd_mm: str,
    end_dd_mm: str,
    func,
    year_minus: int = 0,
):
    results = pd.DataFrame(
        columns=[
            "station id",
            "r_value",
            "gradient",
            "intercept",
            "p_value",
            "conclusion",
        ]
    )
    df = df_moisture.copy()
    for station in df.STATIONS_ID.unique():
        save_station = station
        df = df_moisture.copy()
        df = df[df["STATIONS_ID"] == station]
        df = df[df["hour"].isin([3, 6, 9, 12, 15, 18, 21])]
        df = select_time_range(df, start_dd_mm=start_dd_mm, end_dd_mm=end_dd_mm)
        df["useful_humidity"] = df.RF_STD.apply(func)

        df = df.groupby(["year"]).mean().reset_index()

        x = [i - year_minus for i in df.year]
        y = df.useful_humidity
        gradient, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        if p_value < 0.05 and gradient > 0:
            verdict = "significant"
        elif p_value < 0.05 and gradient < 0:
            verdict = "significant but decreasing risk"
        elif p_value >= 0.05:
            verdict = "non-significant"
        else:
            verdict = "unforseen case"

        results_new_row = pd.DataFrame(
            {
                "station id": [save_station],
                "r_value": [r_value],
                "gradient": [gradient],
                "intercept": [intercept],
                "p_value": [p_value],
                "conclusion": [verdict],
            }
        )
        results = pd.concat([results, results_new_row], ignore_index=True)
    return results


def linear_model_combined(
    df_airtemp: pd.DataFrame,
    df_moisture: pd.DataFrame,
    start_dd_mm: str,
    end_dd_mm: str,
    func1,
    func2,
    year_minus: int = 0,
):
    results = pd.DataFrame(
        columns=[
            "station id",
            "r_value",
            "gradient",
            "intercept",
            "p_value",
            "conclusion",
        ]
    )

    # Step 1: create the time intervals from the input "dd.mm"
    df_airtemp = select_time_range(
        df_airtemp, start_dd_mm=start_dd_mm, end_dd_mm=end_dd_mm
    )
    df_moisture = select_time_range(
        df_moisture, start_dd_mm=start_dd_mm, end_dd_mm=end_dd_mm
    )
    # Step 2: apply disease models
    # Step 2.1: merge the dataframes on the needed parameters
    common_cols = ["MESS_DATUM", "STATIONS_ID", "year", "month", "day", "hour"]
    df_merged = df_airtemp.merge(
        df_moisture,
        how="left",
        on=["MESS_DATUM", "STATIONS_ID", "year", "month", "day", "hour"],
    )
    df_merged = df_merged[common_cols + ["TT_TU", "RF_STD"]]
    # Step 2.2: the model for temperature
    df_merged["t_risk"] = df_merged.TT_TU.apply(func1)

    # Step 2.3: the model for moisture
    df_merged["rh_risk"] = df_merged.RF_STD.apply(func2)

    # Step 2.4: overall risk (combined)
    df_merged["combined_risk"] = df_merged.apply(
        lambda x: (x["rh_risk"] * x["t_risk"]), axis=1
    )

    df = df_merged.copy()
    for station in df.STATIONS_ID.unique():
        save_station = station
        df = df_merged.copy()

        # Selecting the station from the dataframe
        df = df[df["STATIONS_ID"] == station]

        # Grouping by year
        df = df.groupby(["year"]).mean().reset_index()

        # Calibrating the model
        x = [i - year_minus for i in df.year]

        # Taking y for the model
        y = df.combined_risk
        gradient, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        if p_value < 0.05 and gradient > 0:
            verdict = "significant"
        elif p_value < 0.05 and gradient < 0:
            verdict = "significant but decreasing risk"
        else:  # p_value > 0.05:
            verdict = "non-significant"

        results_new_row = pd.DataFrame(
            {
                "station id": [save_station],
                "r_value": [r_value],
                "gradient": [gradient],
                "intercept": [intercept],
                "p_value": [p_value],
                "conclusion": [verdict],
            }
        )
        results = pd.concat([results, results_new_row], ignore_index=True)
    return results
