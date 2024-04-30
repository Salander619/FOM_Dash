""" Page of the sensitivity curves """

# dash
import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

# plotly
import plotly.graph_objects as go

# common
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline as spline
import h5py

# homemade import
# pylint: disable=import-error
from fomweb import sensitivity
from fomweb import analytic_noise
from fomweb import utils
from config_manager import ConfigManager # pylint: disable=import-error

##############################################################################

dash.register_page(__name__)

### data init

# resolved binaries configuration manager
conf_manager = ConfigManager('SO1.sensitivity.resolved_binaries')

# verification GB reader
input_gb_filename = "data/VGB.npy"

gb_config_file = np.load(input_gb_filename)

list_of_names = gb_config_file["Name"]

list_of_names_opt = list_of_names
list_of_names_opt = np.append("select all",list_of_names_opt)

##############################################################################
# layout of the page
layout = html.Div([ # pylint: disable=unused-variable
    html.H1('Sensitivity curves'),

    html.P('Binaries selection'),
    dcc.Checklist(id="binaries_selector",
                  options=['Verification binaries',
                           'Resolved binaries',
                           'Stellar mass binaries',
                           'Massive black hole',
                           'Multiband sources'],
                  value=['Verification binaries'],
                  inline=True,
                 ),

    html.P(""),
    html.P('Sources selection'),

    dcc.Dropdown(id="gb_selector",
                 options=list_of_names_opt,
                 value='select all',
                 multi=True,
                 placeholder="Select galactic binaries"),

    dcc.Graph(
        id="sensitivity_graph",
        figure={
            "layout": {
                "height": 700,  # px
            },
        }),
    dcc.Graph(
        id="sensitivity_graph_2",
        figure={
            "layout": {
                "height": 700,  # px
            },
        }),

    dbc.Nav(
        [
            html.Div(
                dbc.NavLink(
                    "View as notebook",
                    href="https://nbviewer.org/github.com/Salander619/FOM_Dash/blob/main/src/notebooks/sensitivity_plot.ipynb", # pylint: disable=line-too-long
                    active='exact',
                ),
            ),
        ],
        vertical=True,
        pills=True,
    ),
])

##############################################################################

# pylint: disable=unused-variable

# Create plots
@callback(Output("sensitivity_graph", "figure"),
          Output("sensitivity_graph_2", "figure"),
          [Input("config_noise_budget", "data"),
           Input("config_mission_duration","data"),
           Input("gb_selector","value"),
           Input("binaries_selector","value"),
           Input("precalculated_data","on")])
def update_graph(selected_noise_config,
                 selected_duration,
                 selected_gb,
                 binaries_to_display,
                 use_precalculated_data):

    """This function return the sensitivity curves
    
    :param string config_noise_budget: noise configuration choosen with 
        radio button in the sidebar
    :param float config_mission_duration: duration selected with the 
        radio button in the sidebar
    :param list gb_selector: list of verification binaries to display
        on the plot, selected with the dropdown menu in the layout
    :param list binaries_selector: list of binaries to display on the plot,
        selected with the checklist on the layout
    :param boolean precalculated_data: indicate if precalculated table must
        be used, selected with the boolean switch in the sidebar
    
    :return figure sensitivity_graph: sensitivity curve plus galactic binaries 
    :return figure sensitivity_graph_2: sensitivity curve
    """

    mission_duration = selected_duration
    display_mode = "x unified"

    table_verification_gb = []
    table_resolved_gb = []

    if 'Verification binaries' in binaries_to_display:
        if selected_gb is None:
            list_of_gb = []
        else:
            if "select all" in selected_gb:
                list_of_gb = list_of_names
            else:
                list_of_gb = selected_gb

        catalog_selected_gb = [gb for gb in gb_config_file
                               if gb['Name'] in list_of_gb]

        table_verification_gb = sensitivity.compute_gb_sensitivity(
            catalog=catalog_selected_gb,
            noise=selected_noise_config,
            duration=mission_duration
        )

        vf = []
        vy = []
        snr = []

        for vgb in table_verification_gb:
            vf.append(float(vgb["freq"]))
            vy.append(float(np.sqrt(vgb["freq"] * vgb["sh"])))
            snr.append(float(vgb["snr"]))

    if "Resolved binaries" in binaries_to_display:

        input_resolved_binaries_filename = conf_manager.get_data_file(
            (selected_noise_config,str(selected_duration))
        )

        table_resolved_gb = np.load(input_resolved_binaries_filename)

        rb_vf = []
        rb_vy = []

        for vgb in table_resolved_gb:
            rb_vf.append(float(vgb["freq"]))
            rb_vy.append(float(np.sqrt(vgb["freq"] * vgb["sh"])))

    ##########################################################################
    ## prepare the data

    #noise
    noise_instru = analytic_noise.InstrumentalNoise(name=selected_noise_config)
    noise_confu = analytic_noise.ConfusionNoise()

    freq        = np.logspace(-5, 0, 9990)
    duration    = mission_duration  # years
    # to control the +10000

    # noise psd
    sxx_noise_instru_only    = noise_instru.psd(freq,
                                                option="X")
    sxx_confusion_noise_only = noise_confu.psd(freq,
                                               duration=duration,
                                               option="X")
    sxx_noise = sxx_noise_instru_only + sxx_confusion_noise_only

    # response
    r_ = utils.fast_response(freq)
    # NOISE SENSITIVITY
    sh = spline(freq, sxx_noise_instru_only / r_)
    sh_wd = utils.psd2sh(freq, sxx_noise, sky_averaging=False)

    ##########################################################################

    # Plot creation

    ## Figure 1
    fig = go.Figure()

    tmp = list_of_names.tolist()

    if "Resolved binaries" in binaries_to_display:
        fig.add_trace(go.Scatter(
            x=rb_vf,
            y=rb_vy,
            #visible='legendonly',
            mode='markers',
            marker={'color':'blue'},
            marker_symbol="circle",
            name="Resolved GBs",
            hovertemplate = "<b>%{hovertext}</b><br>f= %{x:.4f} Hz<br>h=%{y}",
        ))

    if "Verification binaries" in binaries_to_display:
        fig.add_trace(go.Scatter(
            x=vf,
            y=vy,
            hovertext = tmp,
            #visible='legendonly',
            mode='markers',
            marker={'color':'red',
                    'size':snr},
            marker_symbol="hexagon",
            name="Verification GBs",
            hovertemplate = "<b>%{hovertext}</b><br>f= %{x:.4f} Hz<br>h=%{y}",
        ))

    fig.add_trace(go.Scatter(
        x=freq,
        y=np.sqrt(freq) * np.sqrt(sh(freq)),
        name="Instrumental Noise"
    ))

    fig.add_trace(go.Scatter(
        x=freq,
        y=np.sqrt(freq) * np.sqrt(20 / 3) * np.sqrt(sh_wd(freq)),
        name="LISA Noise (Instru+Confusion)"
    ))

    fig.update_xaxes(title_text="Frequency (Hz)",
                    type="log",
                    showgrid=True,
                    showexponent = 'all',
                    exponentformat='e' )
    fig.update_yaxes(title_text="Characteristic Strain (TODO)",
                    type="log",
                    showgrid=True)
    fig.update_layout(xaxis=dict(range=[-5,0]))
    fig.update_layout(yaxis=dict(range=[-22,-15]))
    fig.update_layout(template="ggplot2")

    fig.update_layout(hovermode=display_mode)

    fig.update_layout(legend=dict(orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                                )
                    )

    fig.update_layout(height=600, width=1000)

    ## Figure 2

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=freq,
        y=sxx_noise_instru_only,
        name="instru"
    ))

    fig2.add_trace(go.Scatter(
        x=freq,
        y=sxx_confusion_noise_only,
        #visible='legendonly',
        name="confusion"
    ))

    fig2.update_xaxes(title_text="Frequency (Hz)",
                    type="log",
                    showgrid=True,
                    showexponent = 'all',
                    exponentformat='e' )
    fig2.update_yaxes(title_text="Characteristic Strain (TODO)",
                    type="log",
                    showgrid=True)

    return fig, fig2
