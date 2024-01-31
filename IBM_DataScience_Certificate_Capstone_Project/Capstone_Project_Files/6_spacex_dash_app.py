# 0 IMPORTS
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# 1 LOADING THE DATA
url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
spacex_df = pd.read_csv(url)
spacex_df.drop('Unnamed: 0', axis=1, inplace=True)

# Setting some variables for the payload range slider
min_payload = int(spacex_df['Payload Mass (kg)'].min())
max_payload = int(spacex_df['Payload Mass (kg)'].max())

# Setting the list of selectable launch sites
launch_sites = spacex_df['Launch Site'].unique().tolist()

# 2 CREATING THE APP
app = dash.Dash(__name__)

# 3 CREATING THE LAYOUT
app.layout = html.Div(children=[
    # Title
    html.H1('Space X Launch Records Dashboard', style={'text-align':'center', 'font-size':24, 'color':'#503D36'}),
    html.Br(),

    # Dropdown - Launch Site selector
    dcc.Dropdown(
        id = 'site-dropdown',
        options = [
            {'label': 'All Sites', 'value':'ALL'},
            {'label': 'CCAFS LC-40', 'value':'CCAFS LC-40'},
            {'label': 'KSC LC-39A', 'value':'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value':'VAFB SLC-4E'},
            {'label': 'CCAFS SLC-40', 'value':'CCAFS SLC-40'}
        ],
        value = 'ALL',
        placeholder= 'Select a Launch Site',
        searchable= True
    ),

    # Placeholder for Pie Chart
    dcc.Graph(id = 'pie-chart'),

    # Range Slider to select the Payload
    html.P('Payload range (Kg):', style={'text-align':'left'}),
    dcc.RangeSlider(
        id = 'payload-slider',
        min= 0, max= 10000, step= 1000,
        marks = {0: '0',
                 2500: '2500',
                 5000: '5000',
                 7500: '7500'},
        value=[min_payload, max_payload],
    ),

    # Placeholder for Scatter Plot
    dcc.Graph(id='success-payload-scatter-chart')
])

# 4 CALLBACKS
# 4.1 CALLBACK TO RENDER SUCCESS-PIE-CHART
@app.callback(
    Output(component_id='pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
# pie chart plotting function
def get_pie_chart(entered_site):

    if entered_site == 'ALL':
        df_all = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            df_all,
            values = 'class',
            names = 'Launch Site',
            title = 'Total Success Launches by Site')

        return fig

    else:
        df_site = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(
            df_site['class'].value_counts(),
            values = 'count',
            names = ['Unsuccessful', 'Successful'],
            title = 'Total Success Launches for site {}'.format(entered_site))

        return fig

# 4.2 CALLBACK TO RENDER THE SUCCESS-PAYLOAD SCATTER PLOT
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')
)
def get_scatter_chart(entered_site, range):
    payload_filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min(range)) & (spacex_df['Payload Mass (kg)'] <= max(range))]

    if entered_site == 'ALL':
        fig = px.scatter(
            payload_filtered_df,
            x = 'Payload Mass (kg)',
            y = 'class',
            color = 'Booster Version Category',
            title = 'Correlation between Payload and Success for all Sites')

        return fig

    else:
        site_filtered = payload_filtered_df[payload_filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_filtered,
            x = 'Payload Mass (kg)',
            y = 'class',
            color = 'Booster Version Category',
            title = 'Correlation between Payload and Success for site {}'.format(entered_site)
        )

        return fig


# 5 RUNNING THE APP
if __name__ == '__main__':
    app.run_server(debug=True, host = '127.0.0.1', port = 8050)