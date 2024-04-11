""" Main page of the app """
import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from PIL import Image

##############################################################################
# Initialize the app
app = Dash(__name__,
           use_pages=True,
           external_stylesheets=[dbc.themes.CERULEAN],
           suppress_callback_exceptions=True)

app.title = 'Wigwag'
app._favicon = ("lisa.ico")

dash.register_page(
    __name__,
    path='/',
    name='Home'
)

image_home_map = Image.open("assets/GW_for_everyone.png")

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
}

sidebar= html.Div(
    [
        html.H2("Navigation and configuration", className="display-6"),
        html.Hr(),
        html.P(
            "Navigation", className="lead"
        ),
        # Navigation without section but automatic
        #dbc.Nav(
        #    [
        #        html.Div(
        #            dbc.NavLink(page['name'],
        #                        href=page["relative_path"],
        #                        active="exact")
        #        )
        #        for page in dash.page_registry.values()
        #   ],
        #    vertical=True,
        #    pills=True,
        #),

        # Navigation with section but manual
        dbc.Nav(
            [
                html.Div(dbc.NavLink("Home",
                                href="/",
                                active="exact")),
                html.Div("SO1: Study the formation and evolution of compact\
                         binary stars and the structure of the Milky Way\
                         Galaxy"),
                html.Div(dbc.NavLink("Sensitivity",
                                href="/sensitivity",
                                active="exact")),
                html.Div("SO2: Trace the origins, growth and merger histories\
                          of massive Black Holes"),
                html.Div(dbc.NavLink("Waterfall",
                                href="/waterfall",
                                active="exact")),
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

    html.Img(src=image_home_map),

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
    app.run(debug=True, port=8051)
