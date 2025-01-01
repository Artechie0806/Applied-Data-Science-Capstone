# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)
launch_site = spacex_df['Launch Site'].unique()
launch_site = list(launch_site) + ['ALL']

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                dcc.Dropdown(id='site-dropdown',
                                             options=[{'label': site, 'value': site} for site in launch_site],
                                             value='ALL',
                                             placeholder="Select a Launch Site",
                                             searchable=True,
                                             style={'width': '50%', 'padding': '3px', 'font-size': '20px', 'text-align': 'center'}
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                                value=[min_payload, max_payload]),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])





# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Group by success/failure across all sites and count success launches
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='Success Count')
        success_counts['Failure Count'] = spacex_df[spacex_df['Launch Site'].isin(success_counts['Launch Site'])]['class'].value_counts().get(0, 0)
        
        # Create pie chart with success count for each launch site
        fig = px.pie(
            success_counts,
            names='Launch Site',
            values='Success Count',
            title='Success vs Failure for All Launch Sites',
            labels={'Success Count': 'Number of Successful Launches'},
        )
    else:
        # Filter the data for the selected site and count successes and failures
        success_counts = spacex_df[spacex_df['Launch Site'] == selected_site]['class'].value_counts()

        # Prepare labels and values for the pie chart
        labels = ['Success', 'Failure']
        values = [success_counts.get(1, 0), success_counts.get(0, 0)]

        # Create pie chart for the specific site
        fig = px.pie(
            names=labels,
            values=values,
            title=f'Success vs Failure for {selected_site} Launch Site',
            labels={'names': 'Outcome', 'values': 'Launch Count'},
        )

    return fig






# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Unpack the payload range
    low, high = payload_range

    # Filter the dataframe based on the selected payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site == 'ALL':
        fig = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class',  # Success/Failure
        color='Booster Version Category',  
        title="Payload Mass vs Success all sites",
        labels={"Payload Mass (kg)": "Payload Mass (kg)", "class": "Success (1) / Failure (0)"},
        hover_data=['Booster Version Category'] 
        )
        return fig
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

        fig = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class',  # Success/Failure
        color='Booster Version Category',  
        title="Payload Mass vs Success all sites",
        labels={"Payload Mass (kg)": "Payload Mass (kg)", "class": "Success (1) / Failure (0)"},
        hover_data=['Booster Version Category'] 
        )

        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
