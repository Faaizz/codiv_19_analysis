import numpy as np
import pandas as pd
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as dhtml
from dash.dependencies import Input, Output

import os

print("Working Directory: {0}".format(os.getcwd()))

df_JH_data= pd.read_csv('data/processed/COVID_final_set.csv', sep=';')

# Create figure
fig= go.Figure()

# Create Dash App
app= dash.Dash()

# Create App layout
app.layout= dhtml.Div([
    dcc.Markdown("""
    # COVID-19 Data Analysis

    Goal of this project is to learn data science methods by applying cross industry 
    standard process for data management (CRISP-DM).

    """),

    dcc.Markdown("""
    ## Multi-Select Country for visualization
    """),

    dcc.Dropdown(
        id='country_dropdown',
        options=[ {'label': each, 'value': each} for each in df_JH_data['country'].unique() ],
        # Default selections
        value= ['Nigeria', 'Germany', 'Italy'],
        multi=True
    ),

    dcc.Markdown("""
    ## Select visualization timeline
    """),

    dcc.Dropdown(
        id= 'visual_time',
        options=[
            {'label': 'Timeline Confirmed', 'value': 'confirmed'},
            {'label': 'Timeline Confirmed Filtered', 'value': 'confirmed_filtered'},
            {'label': 'Timeline Doubling Rate', 'value': 'confirmed_DR'},
            {'label': 'Timeline Doubling Rate Filtered', 'value': 'confirmed_filtered_DR'}
        ],
        value='confirmed',
        multi=False
    ),

    dcc.Graph(figure=fig, id='main_figure')
])


# Add callback for Dropdown

# Callback wrapper
@app.callback(
    Output("main_figure", "figure"),
    [
        Input("country_dropdown", "value"),
        Input('visual_time', 'value')
    ]
)
# Callback function
def update_fig(selected_countries, visual_name):

    # Title
    if('DR' in visual_name):
        my_yaxis={
            'type': 'log',
            'title': 'Approximated doubling rate over 3 days (the larger the number, the better)'
        }
    
    else: 
        my_yaxis={
            'type': 'log',
            'title': 'Confirmed cases (source: Johns Hopkings, log-scale)'
        }

    #Traces
    traces= []
    for country in selected_countries:

        # Selected country mask
        df_plot= df_JH_data[df_JH_data['country']== country]

        # Aggregate country-wide data
        if 'DR' in visual_name:
            # If doubling rate is being calculated, use the mean over the states
            df_plot= df_plot[[
                'date', 'state', 'country', 'confirmed', 'confirmed_filtered', 
                'confirmed_DR', 'confirmed_filtered_DR'
                ]].groupby(['country', 'date']).agg(np.mean).reset_index()

        else:
            # Otherwise, sum up the values for all states
            df_plot= df_plot[[
                'date', 'state', 'country', 'confirmed', 'confirmed_filtered', 
                'confirmed_DR', 'confirmed_filtered_DR'
                ]].groupby(['country', 'date']).agg(np.sum).reset_index()


        # Add a trace
        traces.append(
            {
                "x": df_plot.date,
                "y": df_plot[visual_name],
                "mode":"markers+lines",
                "opacity": 0.8,
                "name": country
            }
        )

    # Layout
    fig_design= dict(
        width=1280,
        height=720,
        xaxis_title="Timeline",
        xaxis={
            "tickangle": -75,
            "nticks": 20,
            "tickfont": dict(size=14, color="#7f7f7f")
        },
        yaxis=my_yaxis
    )

    return {
        "data": traces,
        "layout": fig_design
    }



if __name__ == "__main__":

    app.run_server(debug=True, use_reloader=False)
