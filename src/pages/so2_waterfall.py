""" Page of the waterfall plot """
import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np

from config_manager import ConfigManager # pylint: disable=import-error

##############################################################################

dash.register_page(__name__)

conf_manager = ConfigManager("data/configuration.ini")

##############################################################################

# layout of the page
layout = html.Div([ # pylint: disable=unused-variable
    html.H1('Waterfall plot'),

    dcc.Graph(
        id='waterfall_graph',
        figure={
            "layout": {
                "height": 700,  # px
            },
        }
    ),

    dbc.Nav(
        [
            html.Div(
                dbc.NavLink(
                    "View as notebook",
                    href="https://nbviewer.org/github/Salander619/FOM_Dash/blob/main/src/notebooks/waterfall_plot.ipynb", # pylint: disable=line-too-long
                    active='exact',
                ),
            ),
        ],
        vertical=True,
        pills=True,
    ),
])

##############################################################################
# Create plots

# pylint: disable=unused-variable
@callback(
    Output("waterfall_graph", "figure"),
    Input("config_noise_budget", "data")
)
def update_graph(noise):
    """This function return the waterfall plot
    based on the noise config selected by the user
    
    :param string data_file: path to the data
    
    :return figure waterfall_graph: plot snr 
        based on redshift and total mass"""

    data_file = conf_manager.get_data_file('SO2.waterfall',noise)
    t = np.load(data_file, allow_pickle=True)

    # pylint: disable=unused-variable
    [z_mesh, m_source_mesh, snr_mesh, _, _, _] = t

    sn_cl = np.clip(snr_mesh, 1.0, 4000)
    tickvals = [10, 20, 50, 100, 200, 500, 1000, 4000]
    fig2 = go.Figure(
        data=go.Contour(
            x=m_source_mesh[0, :],
            y=z_mesh[:, 0],
            z=np.log10(sn_cl),
            colorbar=dict(
                title="Signal Noise Ratio",
                titleside="top",
                tickvals=np.log10(tickvals),
                ticktext=tickvals,
            ),
        )
    )
    # update axis of the plot
    fig2.update_xaxes(type="log")
    # update title of axis
    fig2["layout"]["yaxis"].title = "Redshift"
    fig2["layout"]["xaxis"].title = "Total mass"

    return fig2
