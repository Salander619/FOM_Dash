""" Page of the waterfall plot """
import dash
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
import numpy as np

##############################################################################

dash.register_page(__name__)

##############################################################################

# layout of the page
layout = html.Div([
    html.H1('Waterfall plot'),

    dcc.Graph(
        id='waterfall_graph',
        figure={
            "layout": {
                "height": 700,  # px
            },
        }
    )
])

##############################################################################
# Create plots
@callback(Output("waterfall_graph", "figure"),
          [Input("config_noise_budget", "data")])
def update_graph(selected_config):
    if selected_config == "scird":
        fn = "data/data_SO2a_snr_waterfall.c0_scird.pkl"
    else:
        fn = "data/data_SO2a_snr_waterfall.c0.pkl"

    t = np.load(fn, allow_pickle=True)

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