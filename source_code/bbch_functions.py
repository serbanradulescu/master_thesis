import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import seaborn as sns


def quantile_date_stage_crop(crop: str, quantile: float, stage: int):
    if crop not in ["mais", "wheat"]:
        raise ValueError("Crop not found")
    bbch = pd.read_csv("downloads/bbch/bbch_" + crop + ".csv", encoding="latin1")
    stage_date = bbch[bbch["Phase_id"] == stage]
    arr = stage_date.Jultag.to_numpy()
    day_num = str(int(np.quantile(arr, quantile)))
    # adjusting day num
    day_num.rjust(3 + len(day_num), "0")

    # Initialize year
    year = "1950"

    # Initializing start date
    strt_date = date(int(year), 1, 1)

    # converting to date
    res_date = strt_date + timedelta(days=int(day_num) - 1)
    res = res_date.strftime("%d.%m")
    return res


def plot_harvest_date_mais():
    bbch_mais = pd.read_csv("downloads/bbch/bbch_mais.csv", encoding="latin1")
    harvest_date = bbch_mais[(bbch_mais["Phase_id"] == 24)]
    plt.figure(figsize=(15, 7))
    sns.boxenplot(x=harvest_date.Referenzjahr, y=harvest_date.Jultag)
    plt.title(f"Harvesting day in Germany")
    arr = harvest_date.Jultag.to_numpy()
    print("Q1 quantile of arr : ", np.quantile(arr, 0.25))
    print("Q2 quantile of arr : ", np.quantile(arr, 0.50))
    print("Q3 quantile of arr : ", np.quantile(arr, 0.75))
    print("90% of corn is harvested at : ", np.quantile(arr, 0.90))
    print("95% of corn is harvested at : ", np.quantile(arr, 0.95))
    print("99% of corn is harvested at : ", np.quantile(arr, 0.99))


def plot_stage_date_wheat(stage: int):
    # 10 = seeding
    # 12 = bbch10
    # 15 = bbch31
    # 18 = bbch51
    # 19 = bbch75
    # 23 = begin harvesting
    # 24 = harvested
    bbch_mais = pd.read_csv("downloads/bbch/bbch_wheat.csv", encoding="latin1")
    harvest_date = bbch_mais[(bbch_mais["Phase_id"] == stage)]
    plt.figure(figsize=(15, 7))
    sns.boxenplot(x=harvest_date.Referenzjahr, y=harvest_date.Jultag)
    plt.title(f"Harvesting day in Germany")
    arr = harvest_date.Jultag.to_numpy()
    print("Q1 quantile of arr : ", np.quantile(arr, 0.25))
    print("Q2 quantile of arr : ", np.quantile(arr, 0.50))
    print("Q3 quantile of arr : ", np.quantile(arr, 0.75))
    print("90% of wheat reaches bbch51 at : ", np.quantile(arr, 0.90))
    print("95% of wheat reaches bbch51 at : ", np.quantile(arr, 0.95))
    print("99% of wheat reaches bbch51 at : ", np.quantile(arr, 0.99))


def get_phase_definition():
    df = pd.read_csv(
        "https://opendata.dwd.de/climate_environment/CDC/observations_germany/phenology/annual_reporters/crops/recent/PH_Beschreibung_Phasendefinition_Jahresmelder_Landwirtschaft_Kulturpflanze.txt",
        sep=";",
        encoding="latin1",
    )
    return df


def get_bbch(path):
    # mais : https://opendata.dwd.de/climate_environment/CDC/observations_germany/phenology/annual_reporters/crops/historical/PH_Jahresmelder_Landwirtschaft_Kulturpflanze_Mais_1936_2020_hist.txt
    # wheat : https://opendata.dwd.de/climate_environment/CDC/observations_germany/phenology/annual_reporters/crops/historical/PH_Jahresmelder_Landwirtschaft_Kulturpflanze_Winterweizen_1925_2020_hist.txt
    df = pd.read_csv(path, sep=";")
    # df.columns = [col.strip() for col in df.columns]
    return df
