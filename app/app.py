from dash import Dash, dcc, html, Input, Output
import plotly_express as px
import pandas as pd

app = Dash(__name__)

df = pd.read_csv("airtemp.csv")
df = df[["STATIONS_ID", "TT_TU", "year", "day", "month"]]
df["STATIONS_ID"] = df["STATIONS_ID"].apply(lambda x: str(x).zfill(5))
stations_id = df.STATIONS_ID.unique()

data_temperature = {
    station: df[df["STATIONS_ID"] == station] for station in stations_id
}

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
        dcc.Dropdown(options=df.STATIONS_ID.unique(), value="01550", id="stations_id"),
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


@app.callback(
    Output("graph-with-slider", "figure"),
    Input("year-slider", "value"),
    Input("parameter", "value"),
    Input("stations_id", "value"),
    Input("reference_slider", "value"),
)
def update_figure(selected_years, parameter, id, reference):
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
        # fig.update_layout()
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


# df = pd.read_csv("airtemp.csv")
# df = df.groupby("year")
# fig = px.scatter(x=df.index, y=df.TT_TU)


if __name__ == "__main__":
    app.run_server(debug=True)

