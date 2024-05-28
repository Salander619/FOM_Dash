""" Main page of the app """
import configparser
import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from PIL import Image

##############################################################################
# Initialize the app
app = Dash(__name__,
           use_pages=True,
           external_stylesheets=[dbc.themes.CERULEAN],
           suppress_callback_exceptions=True)

app.title = 'LISA Science Explorer'
app._favicon = "LISA_science_explorer_logo.ico" # pylint: disable=protected-access

server = app.server # pylint: disable=unused-variable

dash.register_page(
    __name__,
    path='/',
    name=''
)

image_lisa_logo = Image.open("assets/Logo_LISA_ESA_1711_ImageOnly.png")

# Constants
map_width = 800
map_height = 450
scale_factor = 0.25

config = configparser.ConfigParser()
config.read("data/configuration.ini")

##############################################################################
## creation of widget and styles

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow": "scroll",
}

sidebar= html.Div(
    [
        # Link to the home page
        dbc.Nav(
            html.Div(
                dbc.NavLink("Home map",
                href="/",
                active="exact"),
                style=dict(
                    textAlign='center',
                    fontSize='40px',
                ),
            ),
            vertical=True,
        ),
        html.Hr(),
        html.P(
            "Navigation", className="lead"
        ),

        # Links to other pages sorted by section found in the config.ini file
        dbc.Nav(
            [
                html.Div(
                    [
                        # Section of the pages
                        html.Div(
                            section_name.upper(),
                            id=str("section-"+section_name),
                            style=dict(
                                fontWeight='bold',
                            ),
                        ),
                        dbc.Popover(
                            config["sections"][section_name],
                            target="section-"+section_name,
                            body=True,
                            trigger="hover",
                            offset='0,-200'
                        ),

                        # Links to pages
                        html.Div(
                            [
                                html.Div(
                                    dbc.NavLink(
                                        page['name'][4:],
                                        href=page["relative_path"],
                                        active="exact"),
                                    style=dict(
                                        textAlign='center',
                                    ),
                                )
                                for page in dash.page_registry.values()
                                if page['name'].casefold().startswith(
                                    section_name.casefold(),0,3
                                )
                                # Comparison of SO name must be case
                                # insensitive because key in ini files are in
                                # lower case, SO names in the redbook are
                                # in upper case and dash page registry
                                # only begin with upper case
                            ]
                        )
                    ]
                )
                for section_name in config['sections']
            ],
            vertical=True,
            pills=True,
        ),

        html.P("FOM configuration", className="lead"),

        html.P(""),
        html.P("Noise budget"),
        html.Div(
            dcc.RadioItems(options=['redbook', 'scird'],
                           value='redbook',
                           id='control_noise_budget')
        ),
        html.P(""),
        html.P("Mission duration"),
        dcc.RadioItems(
            id="mission_duration",
            options=[
                {'label': '4.5 years', 'value': 4.5},
                {'label': '7.5 years', 'value': 7.5},
            ],
            value=4.5
        ),
    ],
    style=SIDEBAR_STYLE,
    id="sidebar"
)

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

##############################################################################
## App layout
app.layout = html.Div([
    # title gestion
    html.H1('Welcome to the LISA Science Explorer'),

    # pages gestion
    sidebar,
    dash.page_container,

    dcc.Location(id="url",  refresh="callback-nav"),
    html.Div(
        id="homemap"
    ),

    # storage gestion
    dcc.Store(id='config_noise_budget'),
    dcc.Store(id='config_mission_duration'),
    dcc.Store(id="common_sidebar"),
    dcc.Store(id="precaluled_data"),
], style=CONTENT_STYLE)

##############################################################################
## callback function

# pylint: disable=unused-variable

@callback([Output("mission_duration","options"),
           Output("mission_duration","value")],
          [Input("control_noise_budget","value"),
           Input("mission_duration", "value")])
def display_dropdown(selected_config, selected_duration):
    """
    
    """
    if selected_config == "redbook":
        return [
                {'label': '4.5 years', 'value': 4.5},
                {'label': '7.5 years', 'value': 7.5, 'disabled': True},
            ], 4.5
    else:
        return [
                {'label': '4.5 years', 'value': 4.5},
                {'label': '7.5 years', 'value': 7.5},
            ], selected_duration

# radio button for common config
@callback(
    Output('config_noise_budget', 'data'),
    Input('control_noise_budget', 'value')
)
def get_config_noise(value):
    """ Return the value of the noise budget selector """
    return value

@callback(
    Output('config_mission_duration', 'data'),
    Input('mission_duration', 'value')
)
def get_config_duration(value):
    """ Return the value of the duration selector """
    return value

@callback(
    Output('homemap', 'children'),
    Input('url', 'pathname')
)
def display_homemap(current_path):

    if current_path == "/":

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
        plot_annotes = []

        # pylint: disable=C0209
        # pylint: disable=W1310

        # Fundamental physics
        plot_annotes.append(
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
        plot_annotes.append(
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

        plot_annotes.append(
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

        plot_annotes.append(
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
        plot_annotes.append(
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

        plot_annotes.append(
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

        plot_annotes.append(
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

        plot_annotes.append(
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

        plot_annotes.append(
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

        plot_annotes.append(
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

        plot_annotes.append(
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
        for annotation in plot_annotes:
            fig.add_annotation(x = annotation['x'],
                            y = annotation['y'],
                            text = annotation['text'],
                            showarrow= annotation['showarrow'],
                            xanchor = annotation['xanchor'],
                            yanchor= annotation['yanchor'])

        return dcc.Graph(figure=fig)

##############################################################################
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
