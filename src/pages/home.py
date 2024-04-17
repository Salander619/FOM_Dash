""" Home page of the application """

# dash
import dash
from dash import html, dcc

import plotly.graph_objects as go

from PIL import Image

dash.register_page(__name__)

image_lisa_logo = Image.open("assets/Logo_LISA_ESA_1711_ImageOnly.png")

# Constants
map_width = 800
map_height = 450
scale_factor = 0.25

# Create figure
fig = go.Figure()

# Configure axes
fig.update_xaxes(
    visible=False,
    range=[0, map_width]
)

fig.update_yaxes(
    visible=False,
    range=[0, map_height],
    # the scaleanchor attribute ensures that the aspect ratio stays constant
    scaleanchor="x"
)

# Configure other layout
fig.update_layout(
    width=map_width,
    height=map_height,
    margin={"l": 0, "r": 0, "t": 0, "b": 0},
    template="plotly_white",
)

fig.add_layout_image(
    dict(
        x=map_width * 0.37,
        sizex=map_width * scale_factor,
        y=map_height * 0.6,
        sizey=map_height * scale_factor,
        xref="x",
        yref="y",
        opacity=1.0,
        layer="below",
        sizing="stretch",
        source=image_lisa_logo)
)

# Disable zoom and option that we will not use here
fig.layout.xaxis.fixedrange = True
fig.layout.yaxis.fixedrange = True

# Links management
plotAnnotes = []

# pylint: disable=C0209
# pylint: disable=W1310

# Fundamental physics
plotAnnotes.append(
    dict(
        x=400,
        y=125,
        text="""<a style="font-weight:bold; font-size:20px"
        href="https://arxiv.org/ftp/arxiv/papers/2402/2402.07571.pdf#section.3.5">
        Fundamental physics</a>""".format("Text"),
        showarrow=False,
        xanchor='center',
        yanchor='middle',
    )
)

# Cosmology
plotAnnotes.append(
    dict(
        x=275,
        y=250,
        text="""<a style="font-weight:bold; font-size:20px"
        href="">Cosmology</a>""".format("Text"),
        showarrow=False,
        xanchor='center',
        yanchor='middle',
    )
)

plotAnnotes.append(
    dict(
        x=200,
        y=300,
        text="""<a href=
        "https://arxiv.org/ftp/arxiv/papers/2402/2402.07571.pdf#section.3.6">
        Standard sirens</a>""".format("Text"),
        showarrow=False,
        xanchor='center',
        yanchor='middle',
    )
)

plotAnnotes.append(
    dict(
        x=175,
        y=200,
        text="""<a href=
        "https://arxiv.org/ftp/arxiv/papers/2402/2402.07571.pdf#section.3.7">
        Stochastic background</a>""".format("Text"),
        showarrow=False,
        xanchor='center',
        yanchor='middle',
    )
)

# Astrophysics
plotAnnotes.append(
    dict(
        x=500,
        y=275,
        text="""<a style="font-weight:bold; font-size:20px"
        href="">Astrophysics</a>""".format("Text"),
        showarrow=False,
        xanchor='center',
        yanchor='middle',
    )
)

plotAnnotes.append(
    dict(
        x=400,
        y=325,
        text="""<a href=
        "https://arxiv.org/ftp/arxiv/papers/2402/2402.07571.pdf#section.3.3">
        Extreme mass-ratio inspirals</a>""".format("Text"),
        showarrow=False,
        xanchor='center',
        yanchor='middle',
    )
)

plotAnnotes.append(
    dict(
        x=600,
        y=175,
        text="""<a href=
        "https://arxiv.org/ftp/arxiv/papers/2402/2402.07571.pdf#section.3.4">
        Stellar mass black hole binaries</a>""".format("Text"),
        showarrow=False,
        xanchor='center',
        yanchor='middle',
    )
)

plotAnnotes.append(
    dict(
        x=650,
        y=225,
        text="""<a href="/so2-waterfall">Galactic binaries</a>"""
        .format("Text"),
        showarrow=False,
        xanchor='center',
        yanchor='middle',
    )
)

plotAnnotes.append(
    dict(
        x=700,
        y=325,
        text="""<a href="/so1-sensitivity">LISA GW sources</a>"""
        .format("Text"),
        showarrow=False,
        xanchor='center',
        yanchor='middle',
    )
)

plotAnnotes.append(
    dict(
        x=600,
        y=300,
        text="""<a style="font-weight:bold; font-size:15px" href=
        "https://arxiv.org/ftp/arxiv/papers/2402/2402.07571.pdf#section.3.1">
        Massive black hole binaries</a>""".format("Text"),
        showarrow=False,
        xanchor='center',
        yanchor='middle',
    )
)

plotAnnotes.append(
    dict(
        x=500,
        y=375,
        text="""<a href="/so2-waterfall">
        LISA cosmic horizon</a>""".format("Text"),
        showarrow=False,
        xanchor='center',
        yanchor='middle',
    )
)

# Addition of all the above annotation to the plot
for annotation in plotAnnotes:
    fig.add_annotation(x = annotation['x'],
                       y = annotation['y'],
                       text = annotation['text'],
                       showarrow= annotation['showarrow'],
                       xanchor = annotation['xanchor'],
                       yanchor= annotation['yanchor'])

## App layout
layout = html.Div([
    dcc.Graph(
        figure=fig
    ),
],)
