from typing import Optional
from zipfile import ZipFile
from os.path import exists
from typing import Tuple
import re
import pandas as pd
import wget

# from dwd_data_explore import get_links, common_stations


from source_code.general_functions import get_date


def download_dwd_data(
    parameter: str,
    time: str,
    start_year: int,
    end_year: int,
    dwd_links: dict,
    ids: Optional[str] = None,
    is_test=True,
):
    test_count = 0
    if is_test:
        limit = 4
    else:
        limit = 99999
    df = pd.DataFrame()
    for link in dwd_links[time][parameter]:
        if test_count <= limit:
            test_count += 1
            filename = str.split(link, "/")[-1]
            # Check if the file is in the time range
            if start_year < get_date(filename)[0] or end_year > get_date(filename)[1]:
                continue
            # Check if the id is in the ID list
            if ids != None:
                id = re.findall("_\d{5}_", str(filename))[0][1:-1]
                if id not in ids:
                    continue
            if not exists("downloads/" + time + "/" + parameter + "/" + filename):
                file_zip = wget.download(
                    link, "downloads/" + time + "/" + parameter + "/"
                )
                print("downloading" + filename + "...", end=" ", flush=True)
            else:
                file_zip = "downloads/" + time + "/" + parameter + "/" + filename
                # print("FOUND "+ filename, end =" ", flush=True)
            try:
                with ZipFile(file_zip) as myzip:
                    for filename in myzip.namelist():
                        if "Metadat" not in filename:
                            with myzip.open(filename) as myfile:
                                this_df = pd.read_csv(myfile, sep=";")
                                this_df["STATIONS_ID"] = this_df["STATIONS_ID"].apply(
                                    lambda x: str(x).zfill(5)
                                )
                                df = pd.concat([df, this_df])
            except:
                print("Not able to open:", filename, "Reason: unknown.")
    # Checking if all given ids were found in the data
    if ids != None:
        if len(list(set(ids) - set(df["STATIONS_ID"].unique()))) == 0:
            print("All given ids accounted for")
        else:
            raise ValueError(
                "Not found for id(s):", list(set(ids) - set(df["STATIONS_ID"].unique()))
            )
    if time == "hourly":
        df["year"] = df["MESS_DATUM"].apply(lambda x: str(x)[:4]).astype(int)
        df["month"] = df["MESS_DATUM"].apply(lambda x: str(x)[4:6]).astype(int)
        df["day"] = df["MESS_DATUM"].apply(lambda x: str(x)[6:8]).astype(int)
        df["hour"] = df["MESS_DATUM"].apply(lambda x: str(x)[8:10]).astype(int)
    # Cleaning the white spaces from column names
    df.columns = [col.strip() for col in df.columns]
    # Returning just the years requested
    df = df[df["year"] >= start_year]
    df = df[df["year"] <= end_year]
    return df


# dwd_links = get_links()

# df_airtemp = create_df("air_temperature", "hourly", 1950, 2019, is_test=True)
# print(df_airtemp.head(10))
