from dash import Dash, dcc, html, Input, Output
import plotly_express as px
import pandas as pd

app = Dash(__name__)

df = pd.read_csv("airtemp.csv")
df = df.groupby("year").mean()
# print(df)


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
        dcc.Dropdown(options=df.STATIONS_ID.unique(), value="1550", id="stations_id"),
        html.H4("Select the time range"),
        dcc.RangeSlider(
            min=1950,
            max=2020,
            step=None,
            value=[1970, 2010],
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
        dcc.Graph(id="graph-with-slider"),
    ]
)


@app.callback(
    Output("graph-with-slider", "figure"),
    Input("year-slider", "value"),
    Input("parameter", "value"),
    # Input("stations_id", "value"),
)
def update_figure(selected_years, parameter):  # , id):
    if parameter == "temperature":
        print(selected_years[0], selected_years[1])
        filtered_df = df[
            (df.index >= selected_years[0]) & (df.index <= selected_years[1])
        ]
        # filtered_df = filtered_df[filtered_df["STATIONS_ID"] == id]
        # filtered_df = filtered_df.groupby("year").mean()
        fig = px.line(x=filtered_df.index, y=filtered_df.TT_TU, title="Plot")
        # fig.set_title("mda")
        fig.update_layout(transition_duration=500)
    else:
        fig = px.line(x=[1, 2, 3], y=[3, 4, 5], title="other plot")
    return fig


# df = pd.read_csv("airtemp.csv")
# df = df.groupby("year")
# fig = px.scatter(x=df.index, y=df.TT_TU)


if __name__ == "__main__":
    app.run_server(debug=True)

