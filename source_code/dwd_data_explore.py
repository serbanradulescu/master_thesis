import re
import requests
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt
from typing import List, Tuple
from functools import lru_cache
from requests_html import HTMLSession


@lru_cache  # caching the return of the function for time optimisation; not sure if this function is supported in jupyter notebook
def get_links(
    parameters: Tuple[str] = (
        "air_temperature",
        "dew_point",
        "moisture",
        "precipitation",
    ),  # type: ignore
    time: List[str] = ["1_minute", "5_minutes", "10_minutes", "hourly"],
) -> dict:
    """Return the links from dwd corresponding to the parameters and timeframe we are interested

    Args:
        parameters (tuple[str]): a tuple with the parameters
        time (List[str], optional): the timeframe. Defaults to ["1_minute","5_minutes","10_minutes","hourly"].

    Returns:
        dict: a dictionary containing the links
    """

    dwd_links = {interval: {key: None for key in parameters} for interval in time}
    for interval in time:
        for parameter in parameters:
            url = (
                "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/"
                + str(interval)
                + "/"
                + parameter
                + "/historical/"
            )
            try:
                session = HTMLSession()
                response = session.get(url)
                dwd_links[interval][parameter] = response.html.absolute_links

            except requests.exceptions.RequestException as e:
                print(e)
    return dwd_links


def count_datapoints(
    dwd_links: dict, time, parameter: str, start_year: int, end_year: int
) -> int:
    """Counting the datapoints for a certain parameter

    Args:
        dwd_links (dict): source of data (dwd)
        time (_type_): time period (10_minutes, hourly)
        parameter (str): climatic parameters we are interested in
        start_year (int): start of the observation period
        end_year (int): end of the observation period

    Returns:
        int: numbers of datapoints of the parameter that contain the complete period we are interested
    """
    i = 0
    for link in dwd_links[time][parameter]:
        try:
            # Getting the date from the links
            interval = re.findall("\d{8}", link)
            start_interval = int(interval[0][:4])
            end_interval = int(interval[1][:4])
            # Counting the links that match the requested interval
            if (start_interval <= start_year) & (end_interval >= end_year):
                i = i + 1
        except:
            pass
    return i


def show_available_data(dwd_links: dict, time, parameters: Tuple[str]):
    data_balance = pd.DataFrame(
        columns=parameters,  # type: ignore
        index=[str(i) + "'s - present" for i in range(1950, 2020, 10)],
    )
    for parameter in parameters:
        for i in range(1950, 2020, 10):
            data_balance[parameter][str(i) + "'s - present"] = count_datapoints(
                dwd_links, time, parameter, i, 2020
            )
    return data_balance


def ids_datapoints(
    dwd_links: dict, time: str, parameter: str, start_year: int, end_year: int
) -> List[str]:
    """Returns the ids of the weather station that has entries for the parameter in the mentioned timeframe

    Args:
        dwd_links (dict): source of data (dwd)
        time (str): time period (10_minutes, hourly)
        parameter (str): climatic parameters we are interested in
        start_year (int): start of the observation period
        end_year (int): end of the observation period

    Returns:
        List[str]: ids of weather stations that have the parameter that contain the complete period we are interested
    """
    list = []
    for link in dwd_links[time][parameter]:
        try:
            # Get the date from the links
            interval = re.findall("\d{8}", link)
            start_interval = int(interval[0][:4])
            end_interval = int(interval[1][:4])

            # Get the id from the link
            if (start_interval <= start_year) & (end_interval >= end_year):
                id = re.findall("_\d{5}_", str(link))[0]
                list.append(id[1:-1])
        except:
            pass
    return list


def common_stations(ids_parameter1: List[int], ids_parameter2: List[int]) -> List:
    """Common stations between two parameters, assuming that the time period was previous accounted for.

    Args:
        ids_parameter1 (List[int]): ids of the first parameter
        ids_parameter2 (List[int]): ids of the second parameter

    Returns:
        List: a list with the common ids of the parameters
    """
    list1_as_set = set(ids_parameter1)
    intersection = list1_as_set.intersection(ids_parameter2)
    intersection_as_list = list(intersection)
    return intersection_as_list


def coordinates_stations(ids: List[str], path_info: str):
    df = pd.read_csv(
        path_info, header=None, names=["raw"], sep=";", encoding="latin1", skiprows=2
    )
    # df["id"] = df["raw"].apply(lambda x: x[0:5])
    df["id"] = df["raw"].str.extract(r"(\d{5})")
    # df["period"] = df["raw"].str.findall(r'(\d{8})')
    # df["height"] = df["raw"].str.extract(r'(\s+\d{1,3}\s+)')
    df["coord"] = df["raw"].str.findall(r"(\d{1,2}\.{1}\d{4})")
    df[["lat", "lon"]] = pd.DataFrame(df.coord.tolist(), index=df.index)
    df["lat"] = df["lat"].apply(lambda x: float(x))
    df["lon"] = df["lon"].apply(lambda x: float(x))
    processed_df = df[["id", "lat", "lon"]]
    if ids == None:
        return processed_df
    else:
        return processed_df[processed_df["id"].isin(ids)]


def plot_points_germany(dwd_links):
    """plots the points for"""
    # Preparing the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    countries = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    countries[countries["name"] == "Germany"].plot(color="lightgrey", ax=ax)
    # Plotting for each time range
    for start_year in range(1970, 1949, -10):
        moisture_year_h = ids_datapoints(
            dwd_links, "hourly", "moisture", start_year, 2020
        )
        dew_point_year_h = ids_datapoints(
            dwd_links, "hourly", "dew_point", start_year, 2020
        )
        air_temp_year_h = ids_datapoints(
            dwd_links, "hourly", "air_temperature", start_year, 2020
        )

        common_ids = common_stations(
            common_stations(moisture_year_h, dew_point_year_h), air_temp_year_h  # type: ignore
        )
        stations_coordinates = coordinates_stations(
            common_ids,
            "downloads/hourly/dew_point/TD_Stundenwerte_Beschreibung_Stationen.txt",
        )

        sns.scatterplot(
            x="lon", y="lat", data=stations_coordinates, label=f"{start_year}- 2020"
        )  # ,title=f"Weather stations that measure the parameters required for applying \n the disease models in the time period of {start_year} - present",  ax=ax)

    plt.legend(title="Available data")
    plt.show()


# parameters = ("air_temperature", "dew_point", "moisture", "precipitation")
# dwd_links = get_links(parameters)
# print(dwd_links)
