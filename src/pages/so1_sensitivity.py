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

# lisa import
from fastgb.fastgb import FastGB
import lisaorbits
import lisaconstants

# homemade import
# pylint: disable=import-error
from appFOM import LISA_GB_configuration as myGB
from appFOM import LISA_noise_configuration as NOISE
from appFOM import utils

##############################################################################

dash.register_page(__name__)

### data init
# verification GB reader
input_gb_filename = "data/VGB.npy"

gb_config_file = np.load(input_gb_filename)
nb_of_sources = len(gb_config_file)
GB_out = np.rec.fromarrays(
    [np.zeros((nb_of_sources, 1)),
    np.zeros((nb_of_sources, 1)),
    np.zeros((nb_of_sources, 1))],
    names=["freq", "sh", "snr"]
)

list_of_names = gb_config_file["Name"]

list_of_names_opt = list_of_names
list_of_names_opt = np.append("select all",list_of_names_opt)

list_of_sources = []
list_of_amplitude = []

##############################################################################
# layout of the page
layout = html.Div([ # pylint: disable=unused-variable
    html.H1('Sensitivity curves'),

    html.P('Sources selection'),
    dcc.Store(id='list_of_gb'),

    dcc.Dropdown(id="gb_selector",
                 options=list_of_names_opt,
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
                    href="https://nbviewer.org/github/Salander619/FOM_Dash/blob/main/src/notebooks/sensitivity_plot.ipynb",
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
@callback(Output("sensitivity_graph", "figure"),
          Output("sensitivity_graph_2", "figure"),
          [Input("config_noise_budget", "data"),
           Input("config_mission_duration","data"),
           Input("gb_selector","value")])
def update_graph(selected_noise_config, selected_duration, list_of_gb):
    mission_duration = selected_duration
    if list_of_gb is None:
        list_of_GB = []
    else:
        if "select all" in list_of_gb:
            list_of_GB = list_of_names
        else:
            list_of_GB = list_of_gb
    tdi2 = False
    display_mode = "x unified"

    ##########################################################################
    ## prepare the data

    #noise
    test0 = NOISE.LISA_analytical_noise(selected_noise_config, 42)

    freq        = np.logspace(-5, 0, 9990)
    duration    = mission_duration  # years
    tobs        = duration * lisaconstants.SIDEREALYEAR_J2000DAY * 24 * 60 * 60 # pylint: disable=no-member
    lisa_orbits = lisaorbits.EqualArmlengthOrbits(dt=8640,
                                                size=(tobs + 10000) // 8640)
    # to control the +10000

    # noise psd
    sxx_noise_instru_only    = test0.instru_noise_psd(freq,
                                                    tdi2_=tdi2,
                                                    option_="X")
    sxx_confusion_noise_only =  test0.confusion_noise_psd(freq,
                                                        duration_=duration,
                                                        tdi2_=tdi2,
                                                        option_="X")
    sxx_noise = sxx_noise_instru_only + sxx_confusion_noise_only

    # response
    r_ = utils.fast_response(freq, tdi2=tdi2)
    r = spline(freq, r_)
    # NOISE SENSITIVITY
    sh = spline(freq, sxx_noise_instru_only / r_)
    sh_wd = utils.psd2sh(freq, sxx_noise, sky_averaging=False, tdi2=tdi2)

    #signal
    gb = FastGB(delta_t=15, T=tobs, orbits=lisa_orbits, N=1024)
    df = 1 / tobs

    for j, s in enumerate(gb_config_file):

        pgw = dict(zip(gb_config_file.dtype.names, s))

        if pgw["Name"] in list_of_GB:

            params = np.array( [pgw["Frequency"],
                                pgw["FrequencyDerivative"],
                                pgw["Amplitude"],
                                pgw["EclipticLatitude"],
                                pgw["EclipticLongitude"],
                                pgw["Polarization"],
                                pgw["Inclination"],
                                pgw["InitialPhase"] ])

            source_tmp = myGB.LISA_GB_source(pgw["Name"],params)
            list_of_sources.append(source_tmp)
            list_of_amplitude.append(source_tmp.get_source_parameters()[0][2]
                                    /(1e-23))

            x, _, _, kmin = gb.get_fd_tdixyz(
                source_tmp.get_source_parameters(),
                tdi2=True
            )
            x_f = df * np.arange(kmin, kmin + len(x.flatten()))

            h0 = np.sqrt(4 * df * float(np.sum(np.abs(x) ** 2 / r(x_f))))
            h0 *= np.sqrt(2)
            GB_out["sh"][j] = h0**2
            GB_out["freq"][j] = pgw["Frequency"]

    ##########################################################################
    # display the sensitivity curve
    vf= []
    vy = []

    for vgb in GB_out:
        vf.append(float(vgb["freq"]))
        vy.append(float(np.sqrt(vgb["freq"] * vgb["sh"])))

    ## Figure 1
    fig = go.Figure()

    tmp = list_of_names.tolist()

    fig.add_trace(go.Scatter(
        x=vf,
        y=vy,
        hovertext = tmp,
        #visible='legendonly',
        mode='markers',
        marker={'color':'red'},
        marker_symbol="hexagon",
        name="GBs",
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
