from typing import Tuple
import re
from IPython.display import HTML
import random

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

def hide_toggle(for_next=False):
    this_cell = """$('div.cell.code_cell.rendered.selected')"""
    next_cell = this_cell + '.next()'

    toggle_text = 'Toggle show/hide'  # text shown on toggle link
    target_cell = this_cell  # target cell to control with toggle
    js_hide_current = ''  # bit of JS to permanently hide code in current cell (only when toggling next cell)

    if for_next:
        target_cell = next_cell
        toggle_text += ' next cell'
        js_hide_current = this_cell + '.find("div.input").hide();'

    js_f_name = 'code_toggle_{}'.format(str(random.randint(1,2**64)))

    html = """
        <script>
            function {f_name}() {{
                {cell_selector}.find('div.input').toggle();
            }}

            {js_hide_current}
        </script>

        <a href="javascript:{f_name}()">{toggle_text}</a>
    """.format(
        f_name=js_f_name,
        cell_selector=target_cell,
        js_hide_current=js_hide_current, 
        toggle_text=toggle_text
    )

    return HTML(html)

#print(get_date("https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/moisture/historical/stundenwerte_TF_02947_20061001_20211231_hist.zip"))