# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                   {'label': 'All Sites', 'value': 'ALL'},
                                                   {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                   {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                   {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                   {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                ],
                                             value='ALL',
                                             placeholder="Select a Launch Site here",
                                             searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                
                                
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=0, max=10000, step=1000,marks={0: '0',100: '100'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        
        filtered_df = spacex_df[spacex_df['class'] == 1]
        pie_df = filtered_df.groupby('Launch Site').size().reset_index(name='success_count')

        fig = px.pie(pie_df, 
                     values='success_count', names='Launch Site', title='Total')
        return fig
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        pie_df = site_df['class'].value_counts().reset_index()
        pie_df.columns = ['Outcome', 'Count']  # 0 = Fail, 1 = Success
        pie_df['Outcome'] = pie_df['Outcome'].replace({1: 'Success', 0: 'Failure'})
        fig = px.pie(pie_df,
                 values='Count',
                 names='Outcome',
                 title=f'Success vs Failure Launches for site {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
             [Input(component_id='site-dropdown', component_property='value'), 
               Input(component_id="payload-slider", component_property="value")]
               )
def update_scatter_chart(selected_site, payload_range):
    # 篩選 payload_mass 在 slider 範圍內的資料
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    if selected_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Payload Mass vs Success for All Sites',
                         labels={'class': 'Launch Outcome'})
    else:
        # 先過濾指定 Launch Site
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        
        fig = px.scatter(site_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Payload Mass vs Success for site {selected_site}',
                         labels={'class': 'Launch Outcome'})
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
