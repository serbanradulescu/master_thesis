from dash import Dash, dcc, html, Input, Output
import plotly_express as px
import pandas as pd
import json

app = Dash(__name__)

# Step 1. Preparing the elements for the app

# a. Getting the data:

df = pd.read_csv("/Users/serbanradulescu/Documents/master_thesis/app/airtemp.csv")
df = df[["STATIONS_ID", "TT_TU", "year", "day", "month"]]
df["STATIONS_ID"] = df["STATIONS_ID"].apply(lambda x: str(x).zfill(5))
stations_id = df.STATIONS_ID.unique()

data_temperature = {
    station: df[df["STATIONS_ID"] == station] for station in stations_id
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
    title="Locations in Germany<br>(Hover for id)",
    geo_scope="europe",
    geo=dict(projection_scale=7, center=dict(lat=51.5, lon=10)),
)

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
            marks={
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
            },
        ),
        html.H4("Select the reference period"),
        dcc.RangeSlider(
            min=1950,
            max=2020,
            step=None,
            value=[1960, 1980],
            id="reference_slider",
            marks={
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
            },
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
)
def update_figure(selected_years, parameter, id, reference):
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
        filtered_df = data_temperature[id]
        filtered_df = filtered_df[
            (filtered_df.year >= selected_years[0])
            & (filtered_df.year <= selected_years[1])
        ]
        filtered_df = filtered_df.groupby("year").mean()
        ref_df = filtered_df[
            (filtered_df.index >= reference[0]) & (filtered_df.index <= reference[1])
        ]
        avg_hist = ref_df["TT_TU"].mean()
        max_hist = ref_df["TT_TU"].max()
        min_hist = ref_df["TT_TU"].min()
        filtered_df["7yrs_average"] = filtered_df.TT_TU.rolling(7).mean()
        fig = px.line(
            x=filtered_df.index,
            y=[
                filtered_df.TT_TU,
                filtered_df["7yrs_average"],
                [max_hist for x in filtered_df.TT_TU],
                [avg_hist for x in filtered_df.TT_TU],
                [min_hist for x in filtered_df.TT_TU],
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
