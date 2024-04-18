""" Main page of the app """
import configparser
import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

##############################################################################
# Initialize the app
app = Dash(__name__,
           use_pages=True,
           external_stylesheets=[dbc.themes.CERULEAN],
           suppress_callback_exceptions=True)

app.title = 'Wigwag'
app._favicon = ("lisa.ico")

server = app.server

dash.register_page(
    __name__,
    path='/',
    name=''
)

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
                href="/home",
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
                                for page in dash.page_registry.values() if page['name'].casefold().startswith(section_name.casefold(),0,3)
                                # Comparison of SO name must be case insensitive because key in ini files are lower case,
                                # SO names in the redbook are in upper case and dash page registry only begin with upper case
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
        html.P("Configure noise budget"),
        html.Div(
            dcc.RadioItems(options=['redbook', 'scird'],
                           value='redbook',
                           id='control_noise_budget')
        ),
        html.P("Configure mission duration"),
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
    html.H1('Welcome to Wigwag'),

    # pages gestion
    sidebar,
    dash.page_container,

    # storage gestion
    dcc.Store(id='config_noise_budget'),
    dcc.Store(id='config_mission_duration'),
    dcc.Store(id="common_sidebar"),
], style=CONTENT_STYLE)

##############################################################################
## callback function

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
    """ Return the value of the noise budget selector """
    return value

##############################################################################
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
