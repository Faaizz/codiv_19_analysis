import numpy as np
import pandas as pd
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as dhtml
from dash.dependencies import Input, Output

import os, argparse

#==============================================================================
# COMMAND LINE ARGUMENTS
# Create parser object
cl_parser= argparse.ArgumentParser(
    description="Filter data and compute doubling time."
)

# ARGUMENTS
# Path to data folder
cl_parser.add_argument(
    "--data_path", action="store", default="data/",
    help="Path to data folder"
)

# Collect command-line arguments
cl_options= cl_parser.parse_args()

df_JH_data= pd.read_csv(cl_options.data_path + 'processed/COVID_final_set.csv', sep=';')

# Create figure
fig= go.Figure()

# Create Dash App
app= dash.Dash(external_stylesheets=[dbc.themes.LUX])

# Country List Select
ctry_input= dbc.FormGroup([
    dhtml.H5("Select Countries"),
    dcc.Dropdown(
        id="country_dropdown",
        options=[ {'label': each, 'value': each} for each in df_JH_data['country'].unique() ],
        value=['Nigeria', 'Germany', 'Italy'],
        multi=True
    )    
])

# Visualization Select
vis_input= dbc.FormGroup([
    dhtml.H5("Select Timeline"),
    dcc.Dropdown(
        id="visual_time",
        options=[
            {'label': 'Confirmed Cases', 'value': 'confirmed'},
            {'label': 'Confirmed Cases Filtered', 'value': 'confirmed_filtered'},
            {'label': 'Doubling Rate of Confirmed Cases', 'value': 'confirmed_DR'},
            {'label': 'Doubling Rate of Confirmed Cases Filtered', 'value': 'confirmed_filtered_DR'}
        ],
        value='confirmed',
        multi=False,
        clearable=False
    )    
])

#Create layout
app.layout= dbc.Container(
    fluid=False,
    children=[
        # Navbar
        dbc.NavbarSimple(className="",dark=True,fixed="top",expand="sm",
            style={ "background": "linear-gradient(120deg,#11a048,#01727a)" },
            children=[
                dbc.NavItem(dbc.NavLink("Back to faaizz.com", href="https://faaizz.com"))
            ],
            brand="COVID-19 Dashboard Prototype"
        ),
        # Header
        dhtml.Br(),dhtml.Br(),
        dhtml.Br(),dhtml.Br(),
        dhtml.Br(),dhtml.Br(),
        dhtml.P(children=[
            "A COVID-19 Dashboard Prototype developed using the Cross Industry \
            Standard Process for Data Mining. The data is sourced from ",
            dhtml.A("Johns Hopkings University", href="https://github.com/CSSEGISandData/COVID-19"),
            ", a Savitsky-Golay Filter is used for filtereing (in the filtered versions of the timelines), \
            and the Doubling Times (the estimated number of days it will take for the current number of \
            confirmed cases to get doubled) are calculated using Linear Regression over a window of 3 days."
        ]),
        dhtml.Br(),dhtml.Br(),
        
        # Body
        dbc.Row([
            dbc.Col(md=6, lg=4, children=[ctry_input]),
            dbc.Col(md=6, lg=4, children=[vis_input]),
            dhtml.Br(),dhtml.Br(),
            # Plot
            dbc.Col(sm=12, children=[
                dbc.Col(dhtml.H4("Plots", className="text-center"), sm=12),
                dcc.Graph(figure=fig, id="main_figure")
            ]
            )
        ], className="align-items-center"
        )        
    ],
)

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
            'type': 'linear',
            'title': 'Confirmed cases (source: Johns Hopkings, linear-scale)'
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

    app.run_server(host="0.0.0.0", port="8080", use_reloader=False)
