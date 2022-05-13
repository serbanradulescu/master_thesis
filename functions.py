from typing import Tuple
import re

def get_date(link:str) -> Tuple[int,int]:
    """Returns the years from when the data is available.

    Args:
        link (str): the link that has included the dails for the available data time

    Returns:
        Tuple[int,int]: start time, end time
    """
    m = re.findall('\d{8}', link)
    if m:
        return (int(m[0][:4]),int(m[1][:4]))
    return (0,0)

print(get_date("https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/moisture/historical/stundenwerte_TF_02947_20061001_20211231_hist.zip"))