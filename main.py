# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.figure_factory as ff
import plotly.graph_objects as go
from util import *


tier_dict = {0: "Legend", 1: "Diamond", 2: "Platinum",
             3: "Gold", 4: "Silver", 5: "Bronze"}
num_dict = {"Legend": 0, "Diamond": 1, "Platinum": 2,
            "Gold": 3, "Silver": 4, "Bronze": 5}
star_bonus_dict = {"Bronze 10-Silver 10": 2, "Silver 5": 3,
                   "Gold 10": 4, "Gold 5": 5, "Platinum 10": 6, "Platinum 5": 7, "Diamond 10": 8, "Diamond 5": 9,
                   "Legend": 10, "High Legend": 11}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row(
        html.H1("Hearthstone Simulator")
    ),
    dbc.Row(
        html.H3("One single simulation")
    ),
    dbc.Row([
        dbc.Col(
            dbc.FormGroup([
                dbc.Label("Deck winrate"),
                dbc.Input(id='input1', value=0.55,
                          type='number', min=0, max=1, step="any")
            ])
        ),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label("Starting Tier"),
                dbc.Select(
                    id='input2',
                    options=[{'label': key, 'value': val}
                             for key, val in num_dict.items()
                             if key != "Legend"],
                    value=5
                )
            ])
        ),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label("Starting rank"),
                dbc.Select(
                    id='input3',
                    options=[{'label': x, 'value': x} for x in range(1, 11)],
                    value=10
                )
            ])
        ),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label("Starting stars"),
                dbc.Select(
                    id='input4',
                    options=[{'label': x, 'value': x} for x in range(4)],
                    value='0'
                )
            ])
        ),
        dbc.Col(
            dbc.FormGroup([
                dbc.Label("Previous season rank"),
                dbc.Select(
                    id='input5',
                    options=[{'label': key, 'value': val}
                             for key, val in star_bonus_dict.items()],
                    value=2
                )
            ])
        ),
    ]),
    dcc.Loading(
        id="loading-1",
        type="default",
        children=([
            dbc.Row(
                dcc.Graph(id='single-simulation',
                          style={"display": "block", "width": "100%"})
            ),
            dbc.Row(
                html.Div(id="single-simulation-summary"),
            )
        ])
    ),
    dbc.Row(
        html.H3("10000 simulations"),
        style={
            "marginTop": "20px"
        }
    ),
    dcc.Loading(
        id="loading-2",
        type="default",
        children=[
            dbc.Row(
                dcc.Graph(id='distribution', style={
                    "display": "block", "width": "100%"})

            ), dbc.Row(
                dash_table.DataTable(
                    id='distribution-summary',
                    columns=[{"name": "percentage of players (%)", "id": "quantiles"},
                             {"name": "number of games needed", "id": "data"}],
                    style_data_conditional=[{
                        'if': {
                            'row_index': 4,
                        },
                        'backgroundColor': 'green',
                        'color': 'white'
                    }]
                )
            )
        ]
    )
])


@app.callback(
    [Output(component_id='single-simulation', component_property='figure'),
     Output(component_id='distribution', component_property='figure'),
     Output(component_id='single-simulation-summary',
            component_property='children'),
     Output(component_id='distribution-summary', component_property='data')],
    [Input('input1', 'value'),
     Input('input2', 'value'),
     Input('input3', 'value'),
     Input('input4', 'value'),
     Input('input5', 'value')]
)
def update_output_div(prob, tier, rank, stars, bonus_stars):
    tier, rank, stars, bonus_stars = int(tier), int(
        rank), int(stars), int(bonus_stars)
    stars_needed = convert_tier_rank_stars_to_stars_needed(tier, rank, stars)
    bonus_stars = max(bonus_stars - ((151 - stars_needed)//15), 1)
    win_list = np.random.choice([True, False], (10000, 1000), p=[prob, 1-prob])
    results = np.apply_along_axis(
        simulate_one_game, 1, win_list, stars_needed, bonus_stars)

    # get graph for one simulation
    random_game_results, random_game_num_list = results[0][0], results[0][1]
    x = np.arange(len(random_game_results)+1)
    y = np.asarray(random_game_results)
    fig = go.Figure(data=go.Scatter(
        x=x,
        y=y,
        mode='lines',
        marker=dict(
            color='red',
        )
    ))
    fig.update_layout(
        title='1 random simulation'
    )
    fig.update_xaxes(
        tickvals=random_game_num_list,
        title_text='Games needed for each promotional rank floor'
    )
    fig.update_yaxes(
        ticktext=[tier_dict[convert_stars_needed_to_tier_rank_stars(
            x*15)[0]] + " " + str(convert_stars_needed_to_tier_rank_stars(
                x*15)[1]) for x in range(11)],
        tickvals=[x*15 for x in range(11)],
        title_text='Rank'
    )

    # get summary for 1 simulation
    single_sim_summary = 'You need ' + str(len(random_game_results) - 1) + \
        ' games to reach Legend in this single simulation!'

    # get distribution for x number of simulations
    distribution = np.apply_along_axis(lambda x: len(x[0]), 1, results)
    fig2 = ff.create_distplot(
        [distribution], ["Number of games to get to legend"], bin_size=[10])

    # get summary statistics for distribution
    distribution_summary = []
    for x in range(1, 11):
        distribution_summary.append(
            {"quantiles": x*10, "data": np.quantile(distribution, x*0.1)})

    return fig, fig2, single_sim_summary, distribution_summary


if __name__ == '__main__':
    app.run_server(debug=True)
