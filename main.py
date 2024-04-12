from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import requests
from io import StringIO


data = requests.get("http://localhost:8080/weather").json()
df = pd.json_normalize(data)
df = df.rename(
    columns={
        "city": "Város",
        "time": "Időpont",
        "temperature_2m": "Hőmérséklet (˚C)",
        "precipitation_probability": "Csapadék valószínűsége (%)",
        "precipitation": "Csapadékmennyiség (mm)",
        "cloudcover": "Felhőborítottság (%)",
        "rain": "Eső (mm)",
        "snowfall": "Hó (mm)",
        "windspeed_10m": "Szélerősség (km/h)",
        "winddirection_10m": "Szélirány (˚)",
        "weathercode": "Időjárás kód"
    }
)
df['Időpont'] = pd.to_datetime(df['Időpont'])
df["Időpont"] = df["Időpont"].dt.strftime("%Y-%m-%d %H:%M")

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Supercool Weather App', style={'textAlign':'center'}),
    dcc.Dropdown(df["Város"].unique(), 'Sopron', id='dropdown-selection'),
    dcc.Tabs([
        dcc.Tab(label='Táblázat', children=[
            dash_table.DataTable(data=df[[
                "Város",
                "Időpont",
                "Hőmérséklet (˚C)",
                "Csapadék valószínűsége (%)",
                "Csapadékmennyiség (mm)",
                "Felhőborítottság (%)",
                "Szélerősség (km/h)"
                ]].to_dict('records'), page_size=12, id='table'),
        ]),
        dcc.Tab(label='Grafikonok', children=[
            dcc.Tabs([
                dcc.Tab(label='Hőmérséklet', children=[
                    dcc.Graph(figure={}, id='temp_graph')
                ]),
                dcc.Tab(label='Csapadék', children=[
                    dcc.Graph(figure={}, id='prec_graph')
                ])
            ])
        ])
    ])
])

@callback(
    [
        Output('table', 'data'),
        Output('temp_graph', 'figure'),
        Output('prec_graph', 'figure')
    ],
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df["Város"]==value].iloc[::2, :]
    temp_graph = px.line(dff, x='Időpont', y='Hőmérséklet (˚C)')

    # Create figure with secondary y-axis
    prec_graph = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    prec_graph.add_trace(
        go.Bar(x=dff["Időpont"], y=dff["Csapadékmennyiség (mm)"], name="Csapadékmennyiség (mm)", marker_color='darkblue'),
        secondary_y=False,
    )
    prec_graph.add_trace(
        go.Bar(x=dff["Időpont"], y=dff["Csapadék valószínűsége (%)"], name="Csapadék valószínűsége (%)", opacity=0.2, marker_color='blue'),
        secondary_y=True,
    )
    # Set y-axes titles
    prec_graph.update_yaxes(title_text="Csapadékmennyiség (mm)", secondary_y=False)
    prec_graph.update_yaxes(title_text="Csapadék valószínűsége (%)", secondary_y=True)

    table = dff.to_dict('records')
    return table, temp_graph, prec_graph

if __name__ == '__main__':
    app.run(debug=True)