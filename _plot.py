import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

class SliderInfo():
    def __init__(self, val_list, component_label):
        self.val_list = val_list
        self.component_label = component_label

def draw_by_plotly(ckt):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    freq_list, response_list = ckt.ac_analysis()
    mag_list = 20*np.log10(np.absolute(response_list))
    phase_list = np.angle(response_list, deg=True)
    
    fig.add_trace(
            go.Scatter(
                x=freq_list, y=mag_list,
                mode='lines',
                legendgroup="group1", legendgrouptitle_text=ckt.get_name(),
                name="magnitude",
                line=dict(color='blue')
            )
    )
    fig.add_trace(
            go.Scatter(
                x=freq_list, y=phase_list,
                mode='lines',
                legendgroup="group1",
                name="phase",
                line=dict(color='blue', dash='dot')
            ),
            secondary_y=True
    )

    fig.update_layout(
        legend = {
            "x": 0.01,
            "y": 0.01,
            "groupclick": "toggleitem",
            "bordercolor": "Black",
            "borderwidth": 2
        },
        margin=dict(l=10, r=10, t=10, b=10),
        font={ "size": 16 }
    )

    fig.update_xaxes(type="log", title_text="Frequency(Hz)")
    fig.update_yaxes(title_text="Magnitude(dB)")
    fig.update_yaxes(title_text="Phase(°)", secondary_y=True)

    fig.show()

    return

def slider_draw_by_plotly(ckt, slider_info):
    fig = go.Figure()
    
    for val in slider_info.val_list:
        ckt.set_component_value(slider_info.component_label, val)
        freq_list, response_list = ckt.ac_analysis()
        mag_list = 20*np.log10(np.absolute(response_list))

        fig.add_trace(go.Scatter(x=freq_list, y=mag_list, mode='lines', name=ckt.get_name(), visible=False))

    fig.data[0].visible = True

    steps = []
    for i in range(len(fig.data)):
        step = dict(
            method="update",
            args=[{"visible": [ True if j == i else False for j in range(len(fig.data)) ]}],
            label=f'{slider_info.val_list[i]}'
        )

        steps.append(step)

    sliders = [dict(
        active=0,
        currentvalue={"prefix": f"{slider_info.component_label}: "},
        pad={"t": 50},
        steps=steps
    )]
    
    fig.update_layout(
        sliders=sliders,
        showlegend = True,
        legend = {
            "x": 0.01,
            "y": 0.01,
            "groupclick": "toggleitem",
            "bordercolor": "Black",
            "borderwidth": 2
        },
        margin=dict(l=10, r=10, t=10, b=10),
        font={ "size": 16 }
    )

    fig.update_xaxes(type="log", title_text="Frequency(Hz)")
    fig.update_yaxes(title_text="Magnitude(dB)")

    fig.show()

    return
