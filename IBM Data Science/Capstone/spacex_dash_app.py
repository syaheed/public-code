import pandas as pd
import plotly.express as px
from dash import Dash,html,dcc,Input,Output

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

unique_launch_sites = spacex_df['Launch Site'].unique().tolist()
launch_sites = []
launch_sites.append({'label': 'All Sites', 'value': 'All Sites'})
for launch_site in unique_launch_sites:
    launch_sites.append({'label': launch_site, 'value': launch_site})

marks_dict = {}
for i in range(0,11000,1000):
    marks_dict[i] = {'label': str(i)+' Kg'}

app = Dash(__name__)
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                dcc.Dropdown(
                                    id = 'site-dropdown',
                                    options = launch_sites,
                                    placeholder = 'Select a Launch Site',
                                    searchable = True ,
                                    value = 'All Sites'
                                ),
                                html.Br(),
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                html.P("Payload range (Kg):"),
                                html.Div([
                                    dcc.RangeSlider(
                                        id = 'payload_slider',
                                        min = 0,
                                        max = 10000,
                                        step = 1000,
                                        marks = marks_dict,
                                        value = [min_payload, max_payload]
                                    ),
                                ], style={'padding': '40px 30px'}),
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

@app.callback(
     Output(component_id = 'success-pie-chart', component_property = 'figure'),
     [Input(component_id = 'site-dropdown', component_property = 'value')]
)
def piegraph_update(site_dropdown):
    if site_dropdown == 'All Sites' or site_dropdown == 'None':
        data  = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
                data,
                names = 'Launch Site',
                title = 'Total Success Launches by Site'
            )
    else:
        data = spacex_df.loc[spacex_df['Launch Site'] == site_dropdown]
        fig = px.pie(
                data,
                names = 'class',
                title = 'Total Success Launches for Site ' + site_dropdown,
            )
    return fig

@app.callback(
     Output(component_id = 'success-payload-scatter-chart', component_property = 'figure'),
     [Input(component_id = 'site-dropdown', component_property = 'value'), 
     Input(component_id = "payload_slider", component_property = "value")]
)
def scattergraph_update(site_dropdown, payload_slider):
    low, high = payload_slider
    if (site_dropdown == 'All Sites' or site_dropdown == 'None'):
        print(payload_slider)
        low, high = payload_slider
        data = spacex_df[spacex_df['Payload Mass (kg)'].between(low, high)]
        fig = px.scatter(
                data, 
                x = "Payload Mass (kg)", 
                y = "class",
                title = 'Correlation between Payload and Success for all Sites',
                color = "Booster Version Category"
            )
    else:
        print(payload_slider)
        low, high = payload_slider
        data = spacex_df[spacex_df['Payload Mass (kg)'].between(low, high)]
        data_filtered = data[data['Launch Site'] == site_dropdown]
        fig = px.scatter(
                data_filtered,
                x = "Payload Mass (kg)",
                y = "class",
                title = 'Correlation between Payload and Success for site '+ site_dropdown,
                color = "Booster Version Category"
            )
    return fig


if __name__ == '__main__':
    app.run_server()
