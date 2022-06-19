from dash import Dash, dcc, html, Input, Output
import plotly_express as px
import pandas as pd
import json

app = Dash(__name__)


# Step 1. Preparing the elements for the app
# a. Getting the data:

airtemp_hourly = pd.read_csv(
    "/Users/serbanradulescu/Documents/master_thesis/app/airtemp.csv"
)
airtemp_hourly = airtemp_hourly[["STATIONS_ID", "TT_TU", "year", "day", "month"]]
airtemp_hourly["STATIONS_ID"] = airtemp_hourly["STATIONS_ID"].apply(
    lambda x: str(x).zfill(5)
)
stations_id = airtemp_hourly.STATIONS_ID.unique()

data_temperature = {
    station: airtemp_hourly[airtemp_hourly["STATIONS_ID"] == station]
    for station in stations_id
}

coordinates = pd.read_csv(
    "/Users/serbanradulescu/Documents/master_thesis/app/coordinates.csv"
)
coordinates.id = coordinates.id.apply(lambda x: str(x).zfill(5))

# b. Plotting the map for Germany:
ge_map = px.scatter_geo(
    lon=coordinates.lon, lat=coordinates.lat, hover_name=coordinates.id
)
ge_map.update_layout(
    title="Locations in Germany<br>(click on the map)<br>",
    title_x=0.5,
    geo_scope="europe",
    geo=dict(projection_scale=7, center=dict(lat=51.5, lon=10)),
    clickmode="event+select",
)
ge_map.update_traces(
    marker=dict(size=12, line=dict(width=2, color="DarkSlateGrey")),
    selector=dict(mode="markers"),
)
month_marks = {
    1: "January",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}
year_marks = {
    1950: "1950",
    1955: "",
    1960: "1960",
    1965: "",
    1970: "1970",
    1975: "",
    1980: "1980",
    1985: "",
    1990: "1990",
    1995: "",
    2000: "2000",
    2005: "",
    2010: "2010",
    2015: "",
    2020: "2020",
}

# Step 2: Front-end
app.layout = html.Div(
    [
        html.H2("Effects of climate change on plant disease parameters in Germany"),
        html.H4("Select the parameter"),
        dcc.Dropdown(
            options=[
                {"label": "moisture", "value": "moisture"},
                {"label": "temperature", "value": "temperature"},
            ],
            value="temperature",
            id="parameter",
        ),
        html.H4("Select the ids"),
        # dcc.Dropdown(options=df.STATIONS_ID.unique(), value="01550", id="stations_id"),
        dcc.Graph(figure=ge_map, id="basic-interactions", clickData=None),
        html.H4("Select the time range"),
        dcc.RangeSlider(
            min=1950,
            max=2020,
            step=None,
            value=[1960, 2010],
            id="year-slider",
            marks=year_marks,
        ),
        html.H4("Select the reference period"),
        dcc.RangeSlider(
            min=1950,
            max=2020,
            step=None,
            value=[1960, 1980],
            id="reference_slider",
            marks=year_marks,
        ),
        html.H4("Select the disease parameters"),
        html.H4("Month"),
        dcc.RangeSlider(
            min=1, max=12, step=1, value=[4, 8], marks=month_marks, id="month-slider",
        ),
        dcc.Graph(id="graph-with-slider"),
    ]
)

# Step 3: Back-end


@app.callback(
    Output("graph-with-slider", "figure"),
    Input("year-slider", "value"),
    Input("parameter", "value"),
    Input("basic-interactions", "clickData"),
    Input("reference_slider", "value"),
    Input("month-slider", "value"),
)
def update_figure(selected_years, parameter, id, reference, month):
    if id == None:
        id = "01550"
    else:
        id = id["points"][0]["hovertext"]
    print("id is", id)
    # CASE 1: parameter is temperature
    if parameter == "temperature":

        print(
            selected_years[0],
            selected_years[1],
            id,
            "reference",
            reference[0],
            reference[1],
        )
        df = data_temperature[id]
        df = df[(df.year >= selected_years[0]) & (df.year <= selected_years[1])]
        df = df[(df.month >= month[0]) & (df.month <= month[1])]
        # print(month[0], month[1], filtered_df.month.unique())
        df = df.groupby("year").mean()
        ref_df = df[(df.index >= reference[0]) & (df.index <= reference[1])]
        avg_hist = ref_df["TT_TU"].mean()
        max_hist = ref_df["TT_TU"].max()
        min_hist = ref_df["TT_TU"].min()
        df["7yrs_average"] = df.TT_TU.rolling(7).mean()
        fig = px.line(
            x=df.index,
            y=[
                df.TT_TU,
                df["7yrs_average"],
                [max_hist for x in df.TT_TU],
                [avg_hist for x in df.TT_TU],
                [min_hist for x in df.TT_TU],
            ],
            color_discrete_sequence=["blue", "orange", "red", "green", "black"],
            # template="simple_white",
        )
        newnames = {
            "wide_variable_0": "average_temperature",
            "wide_variable_1": "7yrs_average",
            "wide_variable_2": "historic max",
            "wide_variable_3": "historic average",
            "wide_variable_4": "historic minim",
        }
        fig.for_each_trace(lambda t: t.update(name=newnames[t.name]))
        fig.update_layout(
            title="Average temperatures in Germany point selected",
            xaxis_title="year",
            yaxis_title="% of hours with optimal temperature for Septoria",
            legend_title="Legend",
            transition_duration=500,
            font=dict(family="Courier New, monospace", size=12, color="#4d4d4d"),
        )
    else:
        fig = px.line(x=[1, 2, 3], y=[3, 4, 5], title="other plot")
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
